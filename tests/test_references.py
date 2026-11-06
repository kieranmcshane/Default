"""Checks of the supplied inventory, not of medical completeness."""
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ReferenceTests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads((ROOT / 'data/references.json').read_text())

    def test_seed_matches_inspectable_manifest(self):
        seed = (ROOT / 'web/seed.js').read_text()
        self.assertTrue(seed.startswith('window.EDN_SEED = '))
        embedded = json.loads(seed.removeprefix('window.EDN_SEED = ').strip().removesuffix(';'))
        self.assertEqual(embedded, self.manifest)

    def test_entries_and_source_file_fingerprints(self):
        m = self.manifest
        self.assertEqual(len(m['items']), 51)
        self.assertEqual(len({i['id'] for i in m['items']}), 51)
        for s in m['sources']:
            p = ROOT / s['local_file']
            self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(), s['sha256'])
            self.assertFalse(s.get('current_confirmed', False))

    def test_pulmonary_bis_is_distinct(self):
        items = [i for i in self.manifest['items'] if i['source_id'] == 'cep-paste-2026']
        self.assertEqual(len(items), 22)
        numbered = {i['number']: i for i in items}
        self.assertIn('359', numbered)
        self.assertIn('359 bis', numbered)
        self.assertNotEqual(numbered['359']['id'], numbered['359 bis']['id'])
        self.assertFalse(any('EFR' == i['title'] for i in items))

    def test_neurology_numbers_are_not_invented(self):
        items = [i for i in self.manifest['items'] if i['source_id'] == 'cen-paste-undated']
        self.assertEqual(len(items), 29)
        self.assertTrue(all(i['number'] is None and i['number_status'] == 'unknown' for i in items))
        titles = {i['title'] for i in items}
        self.assertIn('Altération aiguë de la vision', titles)
        self.assertIn('Hémorragie méningée non traumatique', titles)
        self.assertIn('Trouble aigu de la parole. Dysphonie', titles)

    def test_missing_specialties_stay_visible(self):
        missing = {s['specialty'] for s in self.manifest['scope'] if s['status'] == 'source_a_ajouter'}
        self.assertEqual(missing, {'Néphrologie', 'Orthopédie', 'Cancérologie', 'Santé publique'})


if __name__ == '__main__':
    unittest.main()
