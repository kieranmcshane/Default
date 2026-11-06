"""Affiche côte à côte, pour un item, le contenu A/B du CEP 9e et les notes MEA.

Usage : python outils/comparer_item.py 205 [--cep-seul | --mea-seul] [--exclure PEDIATRIE]

- CEP : lignes [A]/[B] de local/cep9/item-XXX.txt, sans le rang C ni les
  « questions tombables » ; passages C retirés à l'intérieur des lignes.
- MEA : notes de local/mea/notes.csv rattachées à l'item, regroupées par verso
  identique (une note TOUR-doublon partage le verso d'une autre).
"""
import argparse
import csv
import re
from collections import OrderedDict
from pathlib import Path


def cep(item: str) -> None:
    lignes = Path(f"local/cep9/item-{item}.txt").read_text(encoding="utf-8").splitlines()
    print(f"===== CEP 9e item {item} (A/B) =====")
    for ligne in lignes:
        if re.search(r"QUESTIONS TOMBABLES", ligne):
            break
        ligne = re.sub(r"\[C\][^\[]*", "", ligne).replace("[A] ", "").strip()
        if not ligne or ligne in ("|", "| |") or "apparaissent en" in ligne:
            continue
        print(ligne)


def mea(item: str, exclure: list[str]) -> None:
    groupes: "OrderedDict[str, dict]" = OrderedDict()
    for r in csv.DictReader(open("local/mea/notes.csv", encoding="utf-8")):
        if item.split("bis")[0] not in r["items"].split():
            continue
        if any(e in r["paquets"] for e in exclure):
            continue
        g = groupes.setdefault(r["verso"], {"nids": [], "q": [], "paquet": r["paquets"].split("::")[-1]})
        g["nids"].append(r["nid"])
        g["q"].append(r["recto"].replace("\n", " "))
    print(f"===== MEA item {item} : {sum(len(g['nids']) for g in groupes.values())} notes, {len(groupes)} versos =====")
    for verso, g in groupes.items():
        print(f"\n## [{g['paquet']}] nids {' '.join(g['nids'])}")
        for q in g["q"]:
            print("Q:", q)
        print("R:", re.sub(r"\n+", " / ", verso))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("item")
    ap.add_argument("--cep-seul", action="store_true")
    ap.add_argument("--mea-seul", action="store_true")
    ap.add_argument("--exclure", nargs="*", default=["PEDIATRIE"])
    a = ap.parse_args()
    if not a.mea_seul:
        cep(a.item)
    if not a.cep_seul:
        mea(a.item, a.exclure)


if __name__ == "__main__":
    main()
