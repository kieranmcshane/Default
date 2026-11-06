"""Contrôle automatique des fichiers d'audit (à lancer avant chaque commit).

Usage :
  python outils/valider_audit.py                 # contrôle tous les items audités
  python outils/valider_audit.py 75 110          # contrôle seulement ces items
  python outils/valider_audit.py --avancement    # tableau d'avancement

Code de sortie 0 = aucune erreur. Les avertissements n'empêchent pas le commit
mais doivent être lus.

Contrôles :
- une ligne et une seule par objectif officiel A/B de l'item (references/cep9/objectifs.csv),
  même identifiant, même rang ; aucun objectif de rang C ;
- statut dans la liste autorisée ; champs obligatoires remplis ; date AAAA-MM-JJ ;
- cohérence statut ↔ corrections (un écart sans correction est refusé) ;
- chaque nid cité existe dans le deck (local/mea/notes.csv) ;
- aucun passage de 15 mots consécutifs copié du référentiel (local/cep9) : le dépôt est public.
"""
import argparse
import csv
import re
import sys
from collections import Counter
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
OBJECTIFS = RACINE / "references/cep9/objectifs.csv"
NOTES = RACINE / "local/mea/notes.csv"
TEXTE_CEP = RACINE / "local/cep9"
DOSSIER = RACINE / "audit/pneumologie"

COLONNES_AUDIT = ["objectif_id", "rang", "rubrique", "intitule", "statut", "notes_mea", "constat",
                  "action", "repere_cep9", "verifie_par", "verifie_le", "relu_par", "relu_le"]
COLONNES_CORR = ["ref", "type", "nid", "objectif_id", "rang", "champ", "actuel", "propose",
                 "justification_cep9"]
STATUTS = {"conforme", "partiel", "à mettre à jour", "non retrouvé", "à vérifier dans Anki",
           "divergent (autre collège)"}
EXIGE_CORRECTION = {"partiel", "à mettre à jour", "non retrouvé", "divergent (autre collège)"}
TYPES = {"modifier", "signaler", "nouvelle"}
N_MOTS_COPIE = 15


def cle_item(item: str) -> str:
    return item.replace(" ", "")


def mots(texte: str) -> list[str]:
    return re.findall(r"[a-zà-öø-ÿœ0-9]+", texte.lower())


def ngrams(liste, n):
    return {" ".join(liste[i:i + n]) for i in range(len(liste) - n + 1)}


def charger_objectifs():
    par_item = {}
    for r in csv.DictReader(open(OBJECTIFS, encoding="utf-8")):
        par_item.setdefault(cle_item(r["item"]), []).append(r)
    return par_item


def charger_notes():
    if not NOTES.exists():
        return None
    return {r["nid"]: r["items"].split() for r in csv.DictReader(open(NOTES, encoding="utf-8"))}


def controler(item, objectifs, notes, erreurs, avert):
    f_audit = DOSSIER / f"item-{item}.csv"
    f_corr = DOSSIER / f"item-{item}-corrections.csv"
    E = lambda m: erreurs.append(f"[{item}] {m}")
    W = lambda m: avert.append(f"[{item}] {m}")

    lecteur = csv.DictReader(open(f_audit, encoding="utf-8"))
    if lecteur.fieldnames != COLONNES_AUDIT:
        E(f"colonnes de {f_audit.name} incorrectes : {lecteur.fieldnames}")
        return
    lignes = list(lecteur)
    attendus = {o["id"]: o for o in objectifs.get(item, [])}
    if not attendus:
        E("item absent de references/cep9/objectifs.csv")
        return
    vus = Counter(l["objectif_id"] for l in lignes)
    for oid, n in vus.items():
        if n > 1:
            E(f"{oid} apparaît {n} fois")
        if oid not in attendus:
            E(f"{oid} n'est pas un objectif officiel de l'item")
    for oid in attendus:
        if oid not in vus:
            E(f"objectif manquant : {oid}")

    corrections = []
    if f_corr.exists():
        lc = csv.DictReader(open(f_corr, encoding="utf-8"))
        if lc.fieldnames != COLONNES_CORR:
            E(f"colonnes de {f_corr.name} incorrectes : {lc.fieldnames}")
        else:
            corrections = list(lc)
    par_obj = Counter(c["objectif_id"] for c in corrections)

    for l in lignes:
        oid = l["objectif_id"]
        o = attendus.get(oid)
        if o and l["rang"] != o["rang"]:
            E(f"{oid} : rang {l['rang']} ≠ rang officiel {o['rang']}")
        if l["rang"] not in ("A", "B"):
            E(f"{oid} : rang {l['rang']} hors périmètre (A/B seulement)")
        if l["statut"] not in STATUTS:
            E(f"{oid} : statut inconnu « {l['statut']} »")
        for champ in ("constat", "action", "repere_cep9", "verifie_par", "verifie_le"):
            if not l[champ].strip():
                E(f"{oid} : champ « {champ} » vide")
        if l["verifie_le"] and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", l["verifie_le"]):
            E(f"{oid} : date verifie_le au mauvais format")
        if l["statut"] == "conforme" and not l["notes_mea"].strip():
            E(f"{oid} : « conforme » sans note citée")
        if l["statut"] == "non retrouvé" and l["notes_mea"].strip():
            W(f"{oid} : « non retrouvé » mais des notes sont citées")
        if l["statut"] in EXIGE_CORRECTION and not par_obj[oid]:
            E(f"{oid} : statut « {l['statut']} » sans ligne dans {f_corr.name}")
        if l["statut"] == "non retrouvé" and not any(
                c["objectif_id"] == oid and c["type"] == "nouvelle" for c in corrections):
            E(f"{oid} : « non retrouvé » sans carte nouvelle proposée")
        for nid in l["notes_mea"].split():
            verifier_nid(nid, item, notes, E, W, oid)

    refs = Counter(c["ref"] for c in corrections)
    for ref, n in refs.items():
        if n > 1:
            E(f"correction {ref} en double")
    for c in corrections:
        ref = c["ref"]
        if c["objectif_id"] not in attendus:
            E(f"correction {ref} : objectif {c['objectif_id']} inconnu")
        if c["type"] not in TYPES:
            E(f"correction {ref} : type « {c['type']} » inconnu")
        if c["type"] in ("modifier", "signaler"):
            if not c["nid"].strip():
                E(f"correction {ref} : nid manquant")
            for nid in c["nid"].split():
                verifier_nid(nid, item, notes, E, W, ref)
            if not c["propose"].strip():
                E(f"correction {ref} : proposition vide")
        if c["type"] == "nouvelle":
            if c["nid"].strip():
                E(f"correction {ref} : une carte nouvelle n'a pas de nid")
            if not re.search(r"Recto\s*:", c["propose"]) or not re.search(r"Verso\s*:", c["propose"]):
                E(f"correction {ref} : la carte nouvelle doit contenir « Recto : … — Verso : … »")
        if not c["justification_cep9"].strip():
            E(f"correction {ref} : justification vide")

    controler_copie(item, lignes, corrections, E)


def verifier_nid(nid, item, notes, E, W, ou):
    if not nid.isdigit():
        E(f"{ou} : nid « {nid} » invalide")
        return
    if notes is None:
        return
    if nid not in notes:
        E(f"{ou} : nid {nid} absent du deck")
    elif re.sub(r"bis$", "", item) not in notes[nid]:
        W(f"{ou} : nid {nid} n'est pas rangé sous l'item (paquets : items {' '.join(notes[nid]) or 'aucun'})")


def controler_copie(item, lignes, corrections, E):
    f = TEXTE_CEP / f"item-{item}.txt"
    if not f.exists():
        return
    source = ngrams(mots(re.sub(r"\[[ABC]\]", " ", f.read_text(encoding="utf-8"))), N_MOTS_COPIE)
    for l in lignes + corrections:
        for champ in ("constat", "action", "propose", "actuel"):
            texte = l.get(champ) or ""
            commun = ngrams(mots(texte), N_MOTS_COPIE) & source
            if commun:
                ident = l.get("objectif_id") if champ in ("constat", "action") else l.get("ref")
                E(f"{ident} / {champ} : {N_MOTS_COPIE} mots copiés du référentiel (« {next(iter(commun))} ») — reformuler")


def avancement(objectifs):
    print("| Item | Objectifs A/B | Statut de l'audit | conforme | partiel | à mettre à jour | non retrouvé | à vérifier dans Anki | divergent | relu |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for item in sorted(objectifs, key=lambda x: (int(re.match(r"\d+", x).group()), x)):
        f = DOSSIER / f"item-{item}.csv"
        n = len(objectifs[item])
        if not f.exists():
            print(f"| {item} | {n} | à faire | | | | | | | |")
            continue
        lignes = list(csv.DictReader(open(f, encoding="utf-8")))
        c = Counter(l["statut"] for l in lignes)
        relu = sum(1 for l in lignes if l["relu_par"].strip())
        print(f"| {item} | {n} | audité | {c['conforme']} | {c['partiel']} | {c['à mettre à jour']} | "
              f"{c['non retrouvé']} | {c['à vérifier dans Anki']} | {c['divergent (autre collège)']} | {relu}/{len(lignes)} |")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("items", nargs="*")
    ap.add_argument("--avancement", action="store_true")
    a = ap.parse_args()
    objectifs = charger_objectifs()
    if a.avancement:
        avancement(objectifs)
        return
    notes = charger_notes()
    erreurs, avert = [], []
    if notes is None:
        avert.append("local/mea/notes.csv absent : nid non vérifiés (voir audit/PROTOCOLE.md, étape 0)")
    if not TEXTE_CEP.exists():
        avert.append("local/cep9 absent : contrôle anti-copie non fait (voir audit/PROTOCOLE.md, étape 0)")
    items = [cle_item(i) for i in a.items] or sorted(
        p.stem.removeprefix("item-") for p in DOSSIER.glob("item-*.csv") if not p.stem.endswith("-corrections"))
    for item in items:
        if not (DOSSIER / f"item-{item}.csv").exists():
            erreurs.append(f"[{item}] fichier audit/pneumologie/item-{item}.csv absent")
            continue
        controler(item, objectifs, notes, erreurs, avert)
    for m in avert:
        print("AVERTISSEMENT", m)
    for m in erreurs:
        print("ERREUR", m)
    print(f"{len(items)} item(s) contrôlé(s) : {len(erreurs)} erreur(s), {len(avert)} avertissement(s)")
    sys.exit(1 if erreurs else 0)


if __name__ == "__main__":
    main()
