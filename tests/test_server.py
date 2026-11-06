"""Functional tests of local-only HTTP import with synthetic text notes."""
import http.client
from http.server import HTTPServer
import json
from pathlib import Path
import sys
import threading
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from lancer import Handler


class LocalServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(('127.0.0.1', 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)

    def request(self, method, path, body=None, headers=None):
        c = http.client.HTTPConnection('127.0.0.1', self.server.server_port, timeout=15)
        try:
            c.request(method, path, body=body, headers=headers or {})
            r = c.getresponse()
            return r.status, dict(r.getheaders()), r.read()
        finally:
            c.close()

    def test_health_and_frontend_are_served(self):
        status, headers, raw = self.request('GET', '/api/health')
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(raw)['mode'], 'local')
        status, headers, raw = self.request('GET', '/')
        self.assertEqual(status, 200)
        self.assertIn('text/html', headers['Content-Type'])
        self.assertIn(b'app.js', raw)

    def test_repository_files_are_not_served(self):
        for path in ['/../README.md', '/README.md', '/data/references.json', '/.git/config']:
            with self.subTest(path=path):
                status, _, _ = self.request('GET', path)
                self.assertEqual(status, 404)

    def test_foreign_host_and_origin_are_rejected(self):
        status, _, _ = self.request('GET', '/', headers={'Host': 'example.org'})
        self.assertEqual(status, 403)
        status, _, _ = self.request('POST', '/api/import?filename=x.txt', b'x',
                                   {'Origin': 'https://example.org'})
        self.assertEqual(status, 403)

    def test_text_import_actual_note_and_metadata(self):
        text = '#separator:tab\n#html:true\n#tags column:3\nQuestion de contrôle\tRéponse synthétique\tEDN::Item_075\n'.encode()
        status, _, raw = self.request('POST', '/api/import?filename=test.tsv', text,
                                      {'Content-Type': 'application/octet-stream'})
        self.assertEqual(status, 200, raw.decode())
        inventory = json.loads(raw)
        self.assertEqual(inventory['schema_version'], 1)
        self.assertEqual(len(inventory['notes']), 1)
        note = inventory['notes'][0]
        self.assertEqual(note['item_candidates'], ['75'])
        self.assertIn('Question de contrôle', [f['text'] for f in note['fields']])

    def test_bad_package_is_an_error_not_empty_success(self):
        status, _, raw = self.request('POST', '/api/import?filename=broken.apkg', b'not a ZIP archive')
        self.assertEqual(status, 422)
        self.assertIn('error', json.loads(raw))

    def test_empty_upload_rejected(self):
        status, _, raw = self.request('POST', '/api/import?filename=x.tsv', b'')
        self.assertEqual(status, 413)


if __name__ == '__main__':
    unittest.main()
