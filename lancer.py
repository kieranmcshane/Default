#!/usr/bin/env python3
"""Ouvre le contrôleur EDN local. Aucun serveur ni compte distant."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parent
WEB = ROOT / 'web'
MAX_UPLOAD = 256 * 1024 * 1024
PUBLIC = {'/': ('index.html', 'text/html; charset=utf-8'),
          '/index.html': ('index.html', 'text/html; charset=utf-8'),
          '/app.js': ('app.js', 'text/javascript; charset=utf-8'),
          '/seed.js': ('seed.js', 'text/javascript; charset=utf-8'),
          '/style.css': ('style.css', 'text/css; charset=utf-8')}


class Handler(BaseHTTPRequestHandler):
    def reply(self, status, content, kind='application/json; charset=utf-8'):
        if isinstance(content, dict):
            content = json.dumps(content, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', kind)
        self.send_header('Content-Length', str(len(content)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.end_headers()
        self.wfile.write(content)

    def local_request(self):
        # No remote hosts, alternate origins or arbitrary filesystem access.
        expected = f'127.0.0.1:{self.server.server_port}'
        if self.headers.get('Host') != expected:
            return False
        origin = self.headers.get('Origin')
        return origin is None or origin == f'http://{expected}'

    def do_GET(self):
        if not self.local_request():
            return self.reply(403, {'error': 'Origine refusée.'})
        path = urlsplit(self.path).path
        if path == '/api/health':
            return self.reply(200, {'status': 'ok', 'mode': 'local', 'schema_version': 1})
        if path not in PUBLIC:
            return self.reply(404, {'error': 'Page inconnue.'})
        name, kind = PUBLIC[path]
        self.reply(200, (WEB / name).read_bytes(), kind)

    def do_POST(self):
        if not self.local_request():
            return self.reply(403, {'error': 'Origine refusée.'})
        req = urlsplit(self.path)
        if req.path != '/api/import':
            return self.reply(404, {'error': 'Route inconnue.'})
        try:
            length = int(self.headers.get('Content-Length', '0'))
        except ValueError:
            return self.reply(400, {'error': 'Taille invalide.'})
        if length <= 0 or length > MAX_UPLOAD:
            return self.reply(413, {'error': 'Fichier vide ou supérieur à 256 Mio. Utilisez la commande import pour les gros paquets.'})
        name = Path(parse_qs(req.query).get('filename', ['export.apkg'])[0]).name
        suffix = Path(name).suffix.lower()
        if suffix not in {'.apkg', '.colpkg', '.anki2', '.anki21', '.txt', '.tsv'}:
            return self.reply(400, {'error': 'Choisissez un paquet Anki ou un export de notes TXT/TSV.'})
        self.connection.settimeout(120)
        try:
            with tempfile.TemporaryDirectory(prefix='edn-import-') as tmp:
                source = Path(tmp) / name
                remaining = length
                with source.open('wb') as stream:
                    while remaining:
                        block = self.rfile.read(min(1024 * 1024, remaining))
                        if not block:
                            raise ValueError('Envoi incomplet.')
                        stream.write(block)
                        remaining -= len(block)
                out = Path(tmp) / 'inventory.json'
                result = subprocess.run([sys.executable, str(ROOT / 'edn_audit.py'), 'import', str(source), '--out', str(out)],
                                        capture_output=True, text=True, timeout=180)
                if result.returncode:
                    return self.reply(422, {'error': (result.stderr or result.stdout or 'Import impossible.')[-2000:]})
                inventory = json.loads(out.read_text(encoding='utf-8'))
                self.reply(200, inventory)
        except (ValueError, OSError, subprocess.TimeoutExpired) as exc:
            self.reply(422, {'error': str(exc)})

    def log_message(self, format, *args):
        # Do not log uploaded content or filenames.
        if args and str(args[0]).startswith('POST'):
            print('Import local terminé.', flush=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--port', type=int, default=8765)
    p.add_argument('--no-browser', action='store_true')
    args = p.parse_args()
    try:
        httpd = HTTPServer(('127.0.0.1', args.port), Handler)
    except OSError as exc:
        p.exit(1, f'Impossible de démarrer : {exc}. Essayez --port 8766.\n')
    url = f'http://127.0.0.1:{httpd.server_port}/'
    print(f'Contrôle EDN — {url}\nGardez cette fenêtre ouverte. Ctrl+C pour arrêter. Aucune donnée envoyée à un service distant.', flush=True)
    if not args.no_browser:
        threading.Timer(0.4, lambda: webbrowser.open(url)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()


if __name__ == '__main__':
    main()
