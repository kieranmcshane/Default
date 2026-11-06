#!/usr/bin/env python3
"""Extract an inspectable, read-only inventory of Anki notes for the EDN audit.

No Anki code, templates, add-ons, JavaScript or media are executed. An inventory
describes supplied files, not the completeness or currency of medical knowledge.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
from html.parser import HTMLParser
import io
import json
import os
from pathlib import Path
import re
import sqlite3
import sys
import tempfile
from datetime import datetime, timezone
import zipfile

MAX_INPUT_BYTES = 1024 * 1024 * 1024
MAX_DATABASE_BYTES = 1024 * 1024 * 1024
MAX_TEXT_BYTES = 128 * 1024 * 1024
MAX_NOTES = 2_000_000
MAX_CARDS = 5_000_000
CHUNK = 1024 * 1024


class ImportFailure(ValueError):
    """A supplied file could not be completely and safely inventoried."""


def canonical_hash(value) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(",", ":")).encode()).hexdigest()


def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(CHUNK), b""):
            h.update(block)
    return h.hexdigest()


class PlainText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.hidden = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}:
            self.hidden += 1
        if not self.hidden and tag in {"br", "p", "div", "li", "tr", "hr"}:
            self.parts.append("\n")
        if not self.hidden and tag == "img":
            attributes = dict(attrs)
            description = attributes.get("src") or "fichier inconnu"
            if attributes.get("alt"):
                description += "; " + attributes["alt"]
            self.parts.append("[image: " + description + "]")
        if not self.hidden and tag in {"audio", "video", "source"}:
            self.parts.append("[média non analysé: " + (dict(attrs).get("src") or tag) + "]")

    def handle_endtag(self, tag):
        if tag in {"script", "style"} and self.hidden:
            self.hidden -= 1
        if not self.hidden and tag in {"p", "div", "li", "tr"}:
            self.parts.append("\n")

    def handle_data(self, text):
        if not self.hidden:
            self.parts.append(text)


def plain_text(value: str, html: bool = True) -> str:
    if html:
        parser = PlainText()
        parser.feed(value)
        parser.close()
        value = "".join(parser.parts)
    value = re.sub(r"\[sound:([^\]]+)\]", r"[audio non analysé: \1]", value)
    return re.sub(r"\n[ \t]*\n(?:[ \t]*\n)+", "\n\n", value).strip()


def normalize_item(number: str, suffix: str = "") -> str | None:
    n = int(number)
    if not 1 <= n <= 367:
        return None
    return str(n) + (" bis" if suffix else "")


def item_candidates(tags: list[str], decks: list[str]) -> list[str]:
    """Only metadata labels supply hints. Incidental note numbers never do."""
    found = set()
    explicit = re.compile(r"(?i)(?<![a-z])(?:items?|edn|ecn|r2c)[\s_:#./-]*0*(\d{1,3})(?:[\s_-]*(bis))?(?!\d)")
    hierarchical = re.compile(r"(?i)(?:^|::)(\d{3})(?:[\s_-]*(bis))?(?=::|$|[ _-])")
    for label in [*tags, *decks]:
        for pattern in [explicit, hierarchical]:
            for match in pattern.finditer(label):
                normalized = normalize_item(*match.groups())
                if normalized:
                    found.add(normalized)
    return sorted(found, key=lambda s: (int(s.split()[0]), "bis" in s))


def make_note(*, digest, source_name, nid, guid, tags, decks, fields, card_count,
              ordinals, model="", raw_fields=None):
    tags = sorted(set(tags))
    decks = sorted(set(decks))
    raw_sha256 = canonical_hash(raw_fields if raw_fields is not None else fields)
    relevant = {"guid": guid, "tags": tags, "decks": decks, "fields": fields, "raw_sha256": raw_sha256,
                "card_count": card_count, "ordinals": sorted(ordinals), "model": model}
    return {"key": digest + ":" + str(nid), "nid": str(nid), "guid": guid,
            "tags": tags, "decks": decks, "fields": fields,
            "sha256": canonical_hash(relevant), "raw_sha256": raw_sha256, "card_count": card_count,
            "item_candidates": item_candidates(tags, decks), "source_file": source_name}


def table_columns(db, name):
    # Fixed, internal identifiers only; never interpolate values from the file.
    if name not in {"notes", "cards", "col", "decks", "fields", "notetypes"}:
        raise ImportFailure("Nom de table inattendu")
    row = db.execute("SELECT type FROM sqlite_master WHERE name=?", (name,)).fetchone()
    if not row or row[0] != "table":
        return set()
    return {row[1] for row in db.execute(f'PRAGMA table_info("{name}")')}


def read_database(path: Path, digest: str, name: str):
    warnings = []
    notes = []
    for suffix in ["-wal", "-journal"]:
        sidecar = Path(str(path) + suffix)
        if sidecar.exists() and sidecar.stat().st_size:
            raise ImportFailure("La collection SQLite possède un journal actif (" + suffix
                                + "). Exportez un paquet .apkg depuis Anki, ou fermez Anki complètement "
                                + "avant l'import ; aucun journal ne sera ignoré ni modifié.")
    uri = path.resolve().as_uri() + "?mode=ro&immutable=1"
    db = sqlite3.connect(uri, uri=True)
    try:
        db.execute("PRAGMA query_only=ON")
        db.execute("PRAGMA trusted_schema=OFF")
        if not {"id", "guid", "mid", "tags", "flds"} <= table_columns(db, "notes"):
            raise ImportFailure("Table notes Anki absente ou schéma non pris en charge")
        if not {"nid", "did", "ord"} <= table_columns(db, "cards"):
            raise ImportFailure("Table cards Anki absente ou schéma non pris en charge")
        note_count = db.execute("SELECT COUNT(*) FROM notes").fetchone()[0]
        if note_count > MAX_NOTES:
            raise ImportFailure(f"Plus de {MAX_NOTES:,} notes : import interrompu")
        if db.execute("SELECT COUNT(*) FROM cards").fetchone()[0] > MAX_CARDS:
            raise ImportFailure(f"Plus de {MAX_CARDS:,} cartes : import interrompu")
        models = {}
        deck_names = {}
        col_columns = table_columns(db, "col")
        if {"models", "decks"} <= col_columns:
            row = db.execute("SELECT models, decks FROM col LIMIT 1").fetchone()
            if row:
                try:
                    models = json.loads(row[0] or "{}")
                    if not isinstance(models, dict) or any(not isinstance(v, dict) for v in models.values()):
                        raise ValueError("Types de notes mal formés")
                    deck_names = {str(k): v.get("name", str(k)) for k, v in json.loads(row[1] or "{}").items()}
                except (ValueError, TypeError, AttributeError):
                    warnings.append("Métadonnées JSON historiques illisibles ; recherche des tables modernes.")
                    models = {}
        if {"id", "name"} <= table_columns(db, "decks"):
            deck_names.update({str(i): n.replace("\x1f", "::") for i, n in db.execute("SELECT id, name FROM decks")})
        modern_fields = {}
        if {"ntid", "ord", "name"} <= table_columns(db, "fields"):
            for ntid, order, field_name in db.execute('SELECT ntid, ord, name FROM fields ORDER BY ntid, ord'):
                modern_fields.setdefault(str(ntid), {})[order] = field_name
        modern_models = {}
        if {"id", "name"} <= table_columns(db, "notetypes"):
            modern_models = {str(i): n for i, n in db.execute("SELECT id, name FROM notetypes")}
        if not models and not modern_fields:
            warnings.append("Noms de champs indisponibles : les champs sont numérotés, leur contenu est conservé.")
        card_index = {}
        card_total = 0
        card_columns = table_columns(db, "cards")
        query = "SELECT nid, did, ord" + (", odid" if "odid" in card_columns else ", 0") + " FROM cards"
        for nid, did, order, original_did in db.execute(query):
            entry = card_index.setdefault(nid, {"decks": set(), "ordinals": []})
            entry["decks"].add(deck_names.get(str(did), f"Paquet {did}"))
            if original_did:
                entry["decks"].add(deck_names.get(str(original_did), f"Paquet {original_did}"))
            entry["ordinals"].append(order)
            card_total += 1
        orphaned = set(card_index)
        seen_ids = set()
        for nid, guid, mid, tag_string, values in db.execute("SELECT id, guid, mid, tags, flds FROM notes ORDER BY id"):
            if nid in seen_ids:
                raise ImportFailure("Base incohérente : identifiant de note dupliqué")
            seen_ids.add(nid)
            if not isinstance(values, str) or not isinstance(tag_string, str):
                raise ImportFailure("Une note contient des champs ou tags non textuels")
            model = models.get(str(mid), {})
            names = {f.get("ord", i): f.get("name", f"Champ {i + 1}") for i, f in enumerate(model.get("flds", []))}
            names.update(modern_fields.get(str(mid), {}))
            fields = [{"name": names.get(i, f"Champ {i + 1}"), "text": plain_text(v)}
                      for i, v in enumerate(values.split("\x1f"))]
            cards = card_index.get(nid, {"decks": [], "ordinals": []})
            orphaned.discard(nid)
            notes.append(make_note(digest=digest, source_name=name, nid=nid, guid=guid,
                                   tags=tag_string.split(), decks=list(cards["decks"]), fields=fields,
                                   card_count=len(cards["ordinals"]), ordinals=cards["ordinals"],
                                   model=model.get("name", modern_models.get(str(mid), str(mid))),
                                   raw_fields=values.split("\x1f")))
        if orphaned:
            raise ImportFailure(f"Base incohérente : {len(orphaned)} références de cartes sans note")
        if not notes:
            warnings.append("Aucune note dans cette base ; ce fichier ne valide aucune couverture.")
        if any(n["card_count"] == 0 for n in notes):
            warnings.append("Certaines notes n'ont aucune carte ; elles ne garantissent pas une révision possible dans Anki.")
        if any(any(marker in f["text"] for marker in ["[image", "[audio non analysé:", "[média non analysé:"])
               for n in notes for f in n["fields"]):
            warnings.append("Images et sons non analysés : vérifier ces médias dans Anki pendant la relecture.")
        return notes, card_total, warnings
    except (sqlite3.Error, TypeError, AttributeError, ValueError) as exc:
        if isinstance(exc, ImportFailure):
            raise
        raise ImportFailure("Base SQLite Anki ou métadonnées illisibles : " + str(exc)) from exc
    finally:
        db.close()


def copy_bounded(source, target, limit):
    total = 0
    while block := source.read(CHUNK):
        total += len(block)
        if total > limit:
            raise ImportFailure("Collection décompressée trop volumineuse (limite 1 Gio)")
        target.write(block)
    return total


def read_package(path: Path, digest: str):
    warnings = []
    try:
        with zipfile.ZipFile(path) as archive, tempfile.TemporaryDirectory(prefix="edn-audit-") as temporary:
            names = archive.namelist()
            candidates = [n for n in ["collection.anki21b", "collection.anki21", "collection.anki2"] if n in names]
            if not candidates:
                raise ImportFailure("Aucune collection Anki reconnue dans l'archive")
            selected = candidates[0]
            if names.count(selected) != 1:
                raise ImportFailure("Archive ambiguë : plusieurs collections portent le même nom")
            info = archive.getinfo(selected)
            if info.file_size > MAX_DATABASE_BYTES:
                raise ImportFailure("Collection archivée trop volumineuse (limite 1 Gio)")
            if info.flag_bits & 1:
                raise ImportFailure("Archive chiffrée non prise en charge")
            destination = Path(temporary) / "collection.sqlite"
            with archive.open(selected) as raw, destination.open("wb") as output:
                if selected.endswith("21b"):
                    try:
                        import zstandard
                    except ImportError as exc:
                        raise ImportFailure("Ce paquet récent nécessite zstandard : python -m pip install -r requirements.txt") from exc
                    try:
                        with zstandard.ZstdDecompressor(max_window_size=MAX_DATABASE_BYTES // 1024).stream_reader(raw) as reader:
                            copy_bounded(reader, output, MAX_DATABASE_BYTES)
                    except zstandard.ZstdError as exc:
                        raise ImportFailure("Collection Zstandard illisible") from exc
                else:
                    copy_bounded(raw, output, MAX_DATABASE_BYTES)
            if selected != "collection.anki2" and "collection.anki2" in names:
                warnings.append("Collection récente utilisée ; la collection de compatibilité .anki2 a été ignorée.")
            notes, cards, more_warnings = read_database(destination, digest, path.name)
            return notes, cards, warnings + more_warnings
    except (zipfile.BadZipFile, RuntimeError, EOFError) as exc:
        raise ImportFailure("Archive Anki invalide : " + str(exc)) from exc


def read_text(path: Path, digest: str):
    if path.stat().st_size > MAX_TEXT_BYTES:
        raise ImportFailure("Export texte trop volumineux (limite 128 Mio)")
    try:
        text = path.read_text(encoding="utf-8-sig")
    except UnicodeError as exc:
        raise ImportFailure("L'export texte doit être encodé en UTF-8") from exc
    lines = text.splitlines(keepends=True)
    headers = {}
    index = 0
    for index, line in enumerate(lines):
        match = re.match(r"^#([a-zA-Z_ ]+):(.*?)(?:\r?\n)?$", line)
        if not match:
            break
        headers[match[1].strip().lower()] = match[2].strip()
    else:
        index = len(lines)
    separator_name = headers.get("separator", "tab").lower()
    separators = {"tab": "\t", "comma": ",", "semicolon": ";", "pipe": "|", "colon": ":", "space": " "}
    if separator_name not in separators:
        raise ImportFailure("Séparateur Anki non pris en charge : " + separator_name)
    separator = separators[separator_name]
    html = headers.get("html", "true").lower() == "true"
    column_names = headers.get("columns", "").split(separator) if headers.get("columns") else []
    special = {}
    for kind in ["tags", "deck", "notetype", "guid"]:
        value = headers.get(kind + " column")
        if value:
            try:
                position = int(value) - 1
                if position < 0:
                    raise ValueError()
                special[kind] = position
            except ValueError as exc:
                raise ImportFailure(f"Numéro de colonne {kind} invalide") from exc
    notes = []
    try:
        reader = csv.reader(io.StringIO("".join(lines[index:])), delimiter=separator, strict=True)
        for row_number, row in enumerate(reader, 1):
            if not row or all(not v for v in row):
                continue
            if len(notes) >= MAX_NOTES:
                raise ImportFailure("Trop de notes dans l'export texte")
            if any(i >= len(row) for i in special.values()):
                raise ImportFailure(f"Ligne {row_number} : une colonne de métadonnées déclarée est absente")
            if column_names and len(row) != len(column_names):
                raise ImportFailure(f"Ligne {row_number} : {len(row)} colonnes au lieu de {len(column_names)}")
            fields = [{"name": column_names[i] if i < len(column_names) else f"Champ {i + 1}",
                       "text": plain_text(value, html=html)}
                      for i, value in enumerate(row) if i not in special.values()]
            if not fields:
                raise ImportFailure("L'export ne contient aucune colonne de contenu")
            get = lambda k: row[special[k]] if k in special else ""
            guid = get("guid")
            # Text exports cannot reliably preserve numeric note ids or card counts.
            notes.append(make_note(digest=digest, source_name=path.name,
                                   nid="txt-" + str(row_number), guid=guid, tags=get("tags").split(),
                                   decks=[get("deck")] if get("deck") else [], fields=fields,
                                   card_count=None, ordinals=[], model=get("notetype"),
                                   raw_fields=[value for i, value in enumerate(row) if i not in special.values()]))
    except csv.Error as exc:
        raise ImportFailure("Export texte mal formé : " + str(exc)) from exc
    warnings = ["Export texte : nombre de cartes et identifiants numériques Anki indisponibles ; les identifiants txt-* désignent les lignes exportées."]
    if "tags" not in special:
        warnings.append("Colonne de tags non déclarée ; elle ne sera pas devinée. Exporter les tags avec les en-têtes Anki pour repérer les items.")
    if not notes:
        warnings.append("Aucune note dans cet export ; ce fichier ne valide aucune couverture.")
    return notes, None, warnings


def import_files(paths, *, force_text=False):
    files = []
    notes = []
    warnings = ["Les indices d'items sont des suggestions issues des tags et paquets, jamais une preuve de couverture ou d'actualité.",
                "L'import complet concerne uniquement les fichiers fournis ; il ne prouve pas que tous les paquets souhaités ont été fournis."]
    digests = set()
    for raw_path in paths:
        path = Path(raw_path)
        if not path.is_file():
            raise ImportFailure("Fichier introuvable : " + str(path))
        if path.stat().st_size > MAX_INPUT_BYTES:
            raise ImportFailure("Fichier trop volumineux (limite 1 Gio) : " + path.name)
        digest = file_hash(path)
        if digest in digests:
            warnings.append("Fichier identique ignoré : " + path.name)
            continue
        digests.add(digest)
        if force_text or path.suffix.lower() in {".txt", ".tsv", ".csv"}:
            extracted, cards, more = read_text(path, digest)
        elif path.suffix.lower() in {".apkg", ".colpkg", ".zip"}:
            extracted, cards, more = read_package(path, digest)
        elif path.suffix.lower() in {".anki2", ".anki21", ".sqlite", ".db"}:
            extracted, cards, more = read_database(path, digest, path.name)
        else:
            raise ImportFailure("Format non pris en charge : " + path.name)
        files.append({"name": path.name, "sha256": digest, "notes": len(extracted), "cards": cards})
        notes.extend(extracted)
        warnings.extend(path.name + " : " + warning for warning in more)
    protected = [n for n in notes if any(t.lower().startswith("ankicollab_protect") for t in n["tags"])]
    if protected:
        warnings.append(f"{len(protected)} note(s) portent un tag Ankicollab_protect : la protection peut empêcher l'application de mises à jour ; vérifier les champs dans Anki.")
    guids = [n["guid"] for n in notes if n["guid"]]
    if len(guids) != len(set(guids)):
        warnings.append("Des GUID de notes sont partagés entre plusieurs entrées : les fichiers peuvent se recouvrir. Ne pas interpréter le total de notes comme un nombre de connaissances distinctes.")
    return {"schema_version": 1, "bundle_sha256": canonical_hash(sorted(digests)),
            "imported_at": datetime.now(timezone.utc).isoformat(), "complete": True,
            "files": files, "notes": notes, "warnings": warnings}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Inventaire local des notes Anki pour l'audit EDN, sans modifier les paquets.")
    sub = parser.add_subparsers(dest="command", required=True)
    extract = sub.add_parser("import", help="Extraire .apkg, .colpkg, SQLite Anki ou export texte UTF-8")
    extract.add_argument("paths", nargs="+", type=Path)
    extract.add_argument("--out", required=True, type=Path, help="Fichier JSON à charger dans l'interface")
    extract.add_argument("--text", action="store_true", help="Interpréter tous les fichiers comme des exports texte Anki")
    args = parser.parse_args(argv)
    try:
        # Guard against accidentally replacing a supplied package with its inventory.
        if args.out.resolve() in {path.resolve() for path in args.paths}:
            raise ImportFailure("Le fichier de sortie ne doit pas remplacer un fichier d'entrée")
        result = import_files(args.paths, force_text=args.text)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        # Replace only a complete output: a failed import never leaves partial JSON.
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=args.out.parent, delete=False) as stream:
            temporary_name = stream.name
            json.dump(result, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        os.replace(temporary_name, args.out)
        print(f"{len(result['notes'])} notes importées depuis {len(result['files'])} fichier(s). Inventaire : {args.out}")
        print("Aucun item n'est déclaré complet ou à jour par cet import.")
        return 0
    except (ImportFailure, OSError) as exc:
        print("Échec de l'import : " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
