#!/usr/bin/env python3
"""Génère une page autonome et une archive du système, sans dépendance externe."""
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'dist'


def build():
    OUT.mkdir(exist_ok=True)
    page = (ROOT / 'web/index.html').read_text(encoding='utf-8')
    style = (ROOT / 'web/style.css').read_text(encoding='utf-8')
    seed = (ROOT / 'web/seed.js').read_text(encoding='utf-8')
    app = (ROOT / 'web/app.js').read_text(encoding='utf-8')
    if '</script' in (seed + app).lower() or '</style' in style.lower():
        raise ValueError('Une fermeture de balise doit être traitée avant incorporation.')
    page = page.replace('<link rel="stylesheet" href="style.css">', '<style>\n' + style + '\n</style>')
    page = page.replace('<script defer src="seed.js"></script><script defer src="app.js"></script>', '')
    page = page.replace('</body>', '<script>\n' + seed + '\n</script><script>\n' + app + '\n</script></body>')
    standalone = OUT / 'Controle-EDN.html'
    standalone.write_text(page, encoding='utf-8')
    archive = OUT / 'controle-edn.zip'
    include = [ROOT / f for f in ['README.md', 'AGENTS.md', '.gitignore', 'requirements.txt', 'edn_audit.py', 'lancer.py', 'construire.py']]
    for directory in ['web', 'data', 'docs', 'sources', 'tests']:
        include += [p for p in (ROOT / directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
        for path in sorted(include):
            z.write(path, 'controle-edn/' + path.relative_to(ROOT).as_posix())
        z.write(standalone, 'controle-edn/Controle-EDN.html')
    print(standalone)
    print(archive)


if __name__ == '__main__':
    build()
