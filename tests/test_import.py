"""Synthetic fixtures exercise real SQLite/ZIP imports, never medical claims."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import edn_audit as audit


class ImportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def make_database(self, name="collection.anki2", *, empty=False, modern=False):
        path = self.root / name
        con = sqlite3.connect(path)
        con.execute("CREATE TABLE notes(id INTEGER PRIMARY KEY, guid TEXT, mid INTEGER, tags TEXT, flds TEXT)")
        con.execute("CREATE TABLE cards(id INTEGER PRIMARY KEY, nid INTEGER, did INTEGER, ord INTEGER, odid INTEGER)")
        con.execute("CREATE TABLE col(models TEXT, decks TEXT)")
        if modern:
            con.execute("INSERT INTO col VALUES('{}', '{}')")
            con.execute("CREATE TABLE decks(id INTEGER, name TEXT)")
            con.execute("INSERT INTO decks VALUES(10, 'EDN\x1fItem_359_bis')")
            con.execute("CREATE TABLE fields(ntid INTEGER, ord INTEGER, name TEXT)")
            con.executemany("INSERT INTO fields VALUES(1,?,?)", [(0, "Recto"), (1, "Verso")])
            con.execute("CREATE TABLE notetypes(id INTEGER, name TEXT)")
            con.execute("INSERT INTO notetypes VALUES(1, 'Cloze')")
        else:
            con.execute("INSERT INTO col VALUES(?,?)", (
                json.dumps({"1": {"name": "Cloze", "flds": [{"ord": 0, "name": "Recto"}, {"ord": 1, "name": "Verso"}]}}),
                json.dumps({"10": {"name": "EDN::Pneumologie::Item_359_bis"}})))
        if not empty:
            con.execute("INSERT INTO notes VALUES(100,'guid-100',1,' Item_075 R2C::359::AB ',?)", (
                '<b>{{c1::Test}}</b><script>secret()</script>\x1f{{c2::Texte}}<img src="x.png" alt="schéma"> [sound:test.mp3]',))
            con.executemany("INSERT INTO cards VALUES(?,100,10,?,0)", [(200, 0), (201, 1)])
        con.commit()
        con.close()
        return path

    def package(self, database, *, name="deck.apkg", member="collection.anki2", extra=None):
        package = self.root / name
        with zipfile.ZipFile(package, "w", zipfile.ZIP_DEFLATED) as archive:
            archive.write(database, member)
            if extra:
                for key, data in extra.items():
                    archive.writestr(key, data)
        return package

    def test_legacy_zip_notes_cards_hints_and_no_execution(self):
        db = self.make_database()
        original = db.read_bytes()
        package = self.package(db, extra={"../../escape.txt": "untrusted", "media": "{}"})
        result = audit.import_files([package])
        self.assertTrue(result["complete"])
        self.assertEqual(len(result["notes"]), 1)
        note = result["notes"][0]
        self.assertEqual(note["card_count"], 2)
        self.assertEqual(result["files"][0]["cards"], 2)
        self.assertEqual(note["item_candidates"], ["75", "359", "359 bis"])
        self.assertEqual(note["nid"], "100")
        self.assertIn("{{c1::Test}}", note["fields"][0]["text"])
        self.assertNotIn("secret", json.dumps(note))
        self.assertIn("[image: x.png; schéma]", note["fields"][1]["text"])
        self.assertIn("[audio non analysé: test.mp3]", note["fields"][1]["text"])
        self.assertEqual(db.read_bytes(), original)
        self.assertFalse((self.root.parent / "escape.txt").exists())

    @unittest.skipUnless(importlib.util.find_spec("zstandard"), "zstandard absent")
    def test_modern_zstd_preferred_over_dummy_and_fields_extracted(self):
        import zstandard
        db = self.make_database(modern=True)
        compressed = zstandard.ZstdCompressor().compress(db.read_bytes())
        package = self.root / "modern.apkg"
        with zipfile.ZipFile(package, "w") as archive:
            archive.writestr("collection.anki2", b"not a real collection, dummy warning")
            archive.writestr("collection.anki21b", compressed)
        result = audit.import_files([package])
        self.assertEqual(len(result["notes"]), 1)
        self.assertEqual(result["notes"][0]["fields"][0]["name"], "Recto")
        self.assertEqual(result["notes"][0]["decks"], ["EDN::Item_359_bis"])
        self.assertTrue(any("compatibilité" in s for s in result["warnings"]))

    def test_anki21_preferred_over_legacy(self):
        db = self.make_database()
        package = self.package(db, member="collection.anki21", extra={"collection.anki2": b"dummy"})
        self.assertEqual(len(audit.import_files([package])["notes"]), 1)

    def test_note_content_numbers_do_not_generate_item_hints(self):
        self.assertEqual(audit.item_candidates([], ["Paquet de 359 questions"]), [])
        self.assertEqual(audit.item_candidates(["Item_359_bis", "Item_3600", "item_000", "2026"], []), ["359 bis"])
        self.assertEqual(audit.item_candidates(["EDN::075::Pneumo"], []), ["75"])

    def test_tsv_headers_multiline_metadata_html_and_unknown_card_counts(self):
        text = self.root / "notes.txt"
        text.write_text('#separator:tab\n#html:true\n#deck column:1\n#notetype column:2\n#guid column:3\n#tags column:6\n#columns:Deck\tType\tGUID\tFront\tBack\tTags\n'
                        'EDN::Item_075\tBasic\tmy-guid\t"<b>Question</b>\nDeuxième ligne"\tRéponse\titem_359_bis\n', encoding="utf-8")
        inventory = audit.import_files([text])
        self.assertEqual(len(inventory["notes"]), 1)
        note = inventory["notes"][0]
        self.assertEqual(note["guid"], "my-guid")
        self.assertEqual(note["fields"][0]["name"], "Front")
        self.assertEqual(note["fields"][0]["text"], "Question\nDeuxième ligne")
        self.assertEqual(note["item_candidates"], ["75", "359 bis"])
        self.assertIsNone(note["card_count"])
        self.assertIsNone(inventory["files"][0]["cards"])
        self.assertEqual(note["nid"], "txt-1")

    def test_tsv_without_headers_does_not_guess_tag_column(self):
        text = self.root / "notes.tsv"
        text.write_text('Question\tRéponse\tItem_359\n', encoding="utf-8")
        note = audit.import_files([text])["notes"][0]
        self.assertEqual(note["item_candidates"], [])
        self.assertEqual(len(note["fields"]), 3)

    def test_invalid_tsv_column_declarations_fail_closed(self):
        text = self.root / "bad.txt"
        text.write_text('#tags column:9\nQuestion\tRéponse\n', encoding="utf-8")
        with self.assertRaises(audit.ImportFailure):
            audit.import_files([text])

    def test_empty_collection_explicit_warning(self):
        db = self.make_database(empty=True)
        result = audit.import_files([db])
        self.assertEqual(result["notes"], [])
        self.assertTrue(any("Aucune note" in s for s in result["warnings"]))

    def test_bundle_is_order_independent_and_duplicates_do_not_inflate(self):
        one = self.root / "one.txt"
        two = self.root / "two.txt"
        one.write_text("A\tB", encoding="utf-8")
        two.write_text("C\tD", encoding="utf-8")
        r1 = audit.import_files([one, two])
        r2 = audit.import_files([two, one, one])
        self.assertEqual(r1["bundle_sha256"], r2["bundle_sha256"])
        self.assertEqual(len(r2["notes"]), 2)
        self.assertEqual(len(set(n["key"] for n in r2["notes"])), 2)

    def test_archive_without_collection_rejected(self):
        package = self.root / "bad.apkg"
        with zipfile.ZipFile(package, "w") as archive:
            archive.writestr("../../collection.anki2", "escape")
        with self.assertRaises(audit.ImportFailure):
            audit.import_files([package])

    def test_oversize_decompression_rejected(self):
        db = self.make_database()
        package = self.package(db)
        with patch.object(audit, "MAX_DATABASE_BYTES", 10):
            with self.assertRaises(audit.ImportFailure):
                audit.import_files([package])

    def test_bad_database_and_archive_fail(self):
        path = self.root / "bad.anki2"
        path.write_text("not sqlite")
        with self.assertRaises(audit.ImportFailure):
            audit.import_files([path])
        path = self.root / "bad.apkg"
        path.write_text("not zip")
        with self.assertRaises(audit.ImportFailure):
            audit.import_files([path])

    def test_duplicate_collection_entry_rejected(self):
        import warnings
        package = self.root / "duplicate.apkg"
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            with zipfile.ZipFile(package, "w") as archive:
                archive.writestr("collection.anki2", b"one")
                archive.writestr("collection.anki2", b"two")
        with self.assertRaises(audit.ImportFailure):
            audit.import_files([package])

    def test_cli_failure_preserves_existing_output_and_input(self):
        invalid = self.root / "invalid.apkg"
        invalid.write_text("not a package")
        output = self.root / "inventory.json"
        output.write_text("preserve")
        self.assertEqual(audit.main(["import", str(invalid), "--out", str(output)]), 2)
        self.assertEqual(output.read_text(), "preserve")
        self.assertEqual(audit.main(["import", str(invalid), "--out", str(invalid)]), 2)
        self.assertEqual(invalid.read_text(), "not a package")

    def test_content_hash_changes_when_note_changes(self):
        db = self.make_database()
        first = audit.import_files([db])
        con = sqlite3.connect(db)
        con.execute("UPDATE notes SET flds='Changed'")
        con.commit()
        con.close()
        second = audit.import_files([db])
        self.assertNotEqual(first["bundle_sha256"], second["bundle_sha256"])
        self.assertNotEqual(first["notes"][0]["sha256"], second["notes"][0]["sha256"])

    def test_raw_html_only_change_invalidates_note_hash(self):
        db = self.make_database()
        first = audit.import_files([db])["notes"][0]
        con = sqlite3.connect(db)
        con.execute("UPDATE notes SET flds=replace(flds, '<b>', '<strong>')")
        con.commit()
        con.close()
        second = audit.import_files([db])["notes"][0]
        self.assertEqual(first["fields"], second["fields"])
        self.assertNotEqual(first["sha256"], second["sha256"])
        self.assertNotEqual(first["raw_sha256"], second["raw_sha256"])

    def test_update_protection_tag_warns(self):
        db = self.make_database()
        con = sqlite3.connect(db)
        con.execute("UPDATE notes SET tags=tags || ' Ankicollab_protect::all '")
        con.commit()
        con.close()
        result = audit.import_files([db])
        self.assertTrue(any("protection peut empêcher" in w for w in result["warnings"]))

    def test_live_wal_collection_rejected_instead_of_ignoring_new_content(self):
        db = self.make_database()
        connection = sqlite3.connect(db)
        try:
            self.assertEqual(connection.execute("PRAGMA journal_mode=WAL").fetchone()[0], "wal")
            connection.execute("UPDATE notes SET flds='New committed content only in WAL'")
            connection.commit()
            self.assertGreater(Path(str(db) + "-wal").stat().st_size, 0)
            with self.assertRaisesRegex(audit.ImportFailure, "Exportez un paquet"):
                audit.import_files([db])
            self.assertEqual(connection.execute("SELECT flds FROM notes").fetchone()[0], "New committed content only in WAL")
        finally:
            connection.close()
        # After SQLite safely closes/checkpoints the DB, the updated content imports.
        result = audit.import_files([db])
        self.assertEqual(result["notes"][0]["fields"][0]["text"], "New committed content only in WAL")


if __name__ == "__main__":
    unittest.main()
