"""Extrait d'un référentiel CEP (DOCX, 9e édition 2026) :

1. le tableau officiel des objectifs (rang, rubrique, intitulé, descriptif) ;
2. le texte de l'item, chaque passage marqué [A], [B] ou [C].

Convention des fichiers CEP 2026 (vérifiée sur les 22 fichiers) :
  rang B = texte bleu 0070C0, rang C = texte vert 00B050, le reste = rang A.

Usage :
  python outils/cep9_extraire.py DOSSIER_DOCX \
      --objectifs references/cep9/objectifs.csv --texte local/cep9

Le texte extrait reste en local (droits du CEP) ; seuls le tableau des
objectifs, les URL et les empreintes SHA-256 sont versionnés.
"""
import argparse
import csv
import hashlib
import re
from pathlib import Path

import docx
from docx.table import Table
from docx.text.paragraph import Paragraph

BLEU_B = {"0070C0"}
VERT_C = {"00B050"}


def item_du_fichier(nom: str) -> str:
    m = re.search(r"Item[-_ ]?(\d+)(bis)?", nom, re.I)
    return (m.group(1) + (" bis" if m.group(2) else "")) if m else nom


def couleur(run, par) -> str | None:
    for source in (run.font, run.style.font if run.style else None, par.style.font if par.style else None):
        if source is not None and source.color is not None and source.color.type is not None:
            try:
                return str(source.color.rgb)
            except Exception:
                return None
    return None


def rang_du_run(run, par) -> str:
    c = (couleur(run, par) or "").upper()
    return "B" if c in BLEU_B else "C" if c in VERT_C else "A"


def segments(par: Paragraph) -> str:
    """Texte du paragraphe avec un marqueur à chaque changement de rang."""
    morceaux, courant = [], None
    for run in par.runs:
        if not run.text:
            continue
        r = rang_du_run(run, par) if run.text.strip() else courant or "A"
        if r != courant:
            morceaux.append(f"[{r}] ")
            courant = r
        morceaux.append(run.text)
    texte = "".join(morceaux).strip()
    if not texte:
        return ""
    if par.style is not None and par.style.name.lower().startswith(("heading", "titre")):
        return "## " + re.sub(r"^\[[ABC]\] ", "", texte)
    return texte


def blocs(document):
    corps = document.element.body
    for enfant in corps.iterchildren():
        tag = enfant.tag.rsplit("}", 1)[-1]
        if tag == "p":
            yield Paragraph(enfant, document)
        elif tag == "tbl":
            yield Table(enfant, document)


def est_tableau_objectifs(table: Table) -> bool:
    try:
        return table.rows[0].cells[0].text.strip().lower() == "rang"
    except IndexError:
        return False


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("dossier", type=Path)
    ap.add_argument("--objectifs", type=Path, required=True)
    ap.add_argument("--texte", type=Path, required=True)
    args = ap.parse_args()
    args.texte.mkdir(parents=True, exist_ok=True)

    lignes = []
    for f in sorted(args.dossier.glob("*.docx")):
        sha = hashlib.sha256(f.read_bytes()).hexdigest()
        item = item_du_fichier(f.name)
        d = docx.Document(str(f))
        sortie = [f"# Item {item} — {f.name}", f"sha256 {sha}", ""]
        n = 0
        for bloc in blocs(d):
            if isinstance(bloc, Paragraph):
                t = segments(bloc)
                if t:
                    sortie.append(t)
            elif est_tableau_objectifs(bloc):
                for row in bloc.rows[1:]:
                    cells = [c.text.strip() for c in row.cells]
                    if len(cells) >= 3 and cells[0] in {"A", "B", "C"}:
                        n += 1
                        lignes.append({
                            "item": item, "id": f"cep9:{item.replace(' ', '')}:{n:02d}",
                            "rang": cells[0], "rubrique": cells[1], "intitule": cells[2],
                            "descriptif": cells[3] if len(cells) > 3 else "",
                            "fichier": f.name, "sha256": sha,
                        })
            else:
                for row in bloc.rows:
                    vus, cellules = set(), []
                    for cell in row.cells:
                        if id(cell._tc) in vus:
                            continue
                        vus.add(id(cell._tc))
                        cellules.append(" ".join(filter(None, (segments(p) for p in cell.paragraphs))))
                    if any(cellules):
                        sortie.append("| " + " | ".join(cellules) + " |")
        (args.texte / f"item-{item.replace(' ', '')}.txt").write_text("\n".join(sortie) + "\n", encoding="utf-8")
        print(f"{f.name}: {n} objectifs")

    args.objectifs.parent.mkdir(parents=True, exist_ok=True)
    with args.objectifs.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(lignes[0]))
        w.writeheader()
        w.writerows(lignes)
    print(f"{len(lignes)} objectifs -> {args.objectifs}")


if __name__ == "__main__":
    main()
