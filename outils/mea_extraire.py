"""Extrait les notes du Deck EDN - MEA (base collection.anki21) en CSV.

Chaque note reçoit la liste des numéros d'item lus dans les noms de ses
paquets (« 🫁188 - Asthme », « 👦🏻203, 359 - Dyspnée laryngée »,
« 👷🏻‍♂️186/188 - … »), toutes spécialités confondues.

Usage :
  python outils/mea_extraire.py collection.anki21 --out local/mea/notes.csv

Pour obtenir collection.anki21 sans télécharger les 1,6 Go de médias,
voir outils/apkg_distant.py.
"""
import argparse
import csv
import html
import json
import re
import sqlite3
from html.parser import HTMLParser
from pathlib import Path

NUM_PAQUET = re.compile(r"^\W*?((?:\d{1,3}\s*(?:,|/|et)\s*)*\d{1,3})\s*[-–]")


class Texte(HTMLParser):
    SAUTS = {"br", "div", "p", "li", "tr", "h1", "h2", "h3", "h4", "ul", "ol", "table"}

    def __init__(self):
        super().__init__()
        self.out = []

    def handle_starttag(self, tag, attrs):
        if tag in self.SAUTS:
            self.out.append("\n")
        elif tag in ("td", "th"):
            self.out.append(" | ")
        elif tag == "img":
            self.out.append("[image]")

    def handle_endtag(self, tag):
        if tag in self.SAUTS:
            self.out.append("\n")

    def handle_data(self, data):
        self.out.append(data)


def texte_brut(valeur: str) -> str:
    p = Texte()
    p.feed(valeur)
    t = html.unescape("".join(p.out))
    t = re.sub(r"\{\{c\d+::(.*?)(::[^}]*)?\}\}", r"\1", t)
    t = re.sub(r"[ \t\xa0]+", " ", t)
    return re.sub(r"\s*\n\s*", "\n", t).strip()


def items_du_paquet(nom: str) -> list[str]:
    nums = []
    for partie in nom.split("::")[2:]:
        m = NUM_PAQUET.match(partie.strip())
        if m:
            nums += [n for n in re.findall(r"\d{1,3}", m.group(1)) if 1 <= int(n) <= 367]
    return nums


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("base", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    db = sqlite3.connect(f"file:{args.base}?mode=ro", uri=True)
    decks_j, models_j = db.execute("select decks, models from col").fetchone()
    paquets = {int(k): v["name"] for k, v in json.loads(decks_j).items()}
    modeles = json.loads(models_j)

    cartes = {}
    for nid, did in db.execute("select nid, did from cards"):
        cartes.setdefault(nid, set()).add(paquets.get(did, "?"))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["nid", "guid", "items", "paquets", "modele", "tour_doublon", "recto", "verso", "extra"])
        for nid, guid, mid, tags, flds in db.execute("select id, guid, mid, tags, flds from notes"):
            m = modeles[str(mid)]
            noms = [f["name"] for f in m["flds"]]
            champs = dict(zip(noms, flds.split("\x1f")))
            recto = champs.get("Recto") or champs.get("Texte") or champs.get("Text") or champs.get("Header", "")
            verso = champs.get("Verso") or champs.get("Extra", "")
            extra = champs.get("Informations supplémentaires") or champs.get("Mnémo") or ""
            decks = sorted(cartes.get(nid, []))
            items = sorted({i for d in decks for i in items_du_paquet(d)}, key=int)
            w.writerow([nid, guid, " ".join(items), " || ".join(decks), m["name"],
                        int("TOUR-doublon" in tags.split()), texte_brut(recto), texte_brut(verso), texte_brut(extra)])
    print(f"notes -> {args.out}")


if __name__ == "__main__":
    main()
