"""Optional browser regression: python tests/browser_smoke.py.

Requires Playwright + Chromium for development only; not needed to run the app.
All notes and medical review statements below are synthetic fixtures.
"""
from __future__ import annotations

import io
import json
import os
from pathlib import Path
import sqlite3
import sys
import tempfile
import threading
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lancer


def package_bytes() -> bytes:
    with tempfile.TemporaryDirectory() as folder:
        db = Path(folder) / 'collection.anki2'
        con = sqlite3.connect(db)
        con.executescript('CREATE TABLE notes(id INTEGER PRIMARY KEY, guid TEXT, mid INTEGER, tags TEXT, flds TEXT);'
                          'CREATE TABLE cards(id INTEGER PRIMARY KEY,nid INTEGER,did INTEGER,ord INTEGER,odid INTEGER);'
                          'CREATE TABLE col(models TEXT,decks TEXT);')
        con.execute('INSERT INTO col VALUES(?,?)', (
            json.dumps({'1': {'flds': [{'name': 'Recto'}]}}),
            json.dumps({'10': {'name': 'Pneumo::Item_075'}})))
        con.execute('INSERT INTO notes VALUES(100,\'guid\',1,\'Item_075\',\'Texte de contrôle synthétique\')')
        con.execute('INSERT INTO cards VALUES(200,100,10,0,0)')
        con.commit()
        con.close()
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, 'w') as archive:
            archive.write(db, 'collection.anki2')
        return stream.getvalue()


def main() -> None:
    from playwright.sync_api import sync_playwright
    server = lancer.HTTPServer(('127.0.0.1', 0), lancer.Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    url = f'http://127.0.0.1:{server.server_port}/'
    try:
        with sync_playwright() as p:
            executable = os.environ.get('EDN_BROWSER_BINARY', '/usr/bin/chromium')
            browser = p.chromium.launch(executable_path=executable, headless=True, args=['--no-sandbox'])
            page = browser.new_page(viewport={'width': 1440, 'height': 1080})
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.goto(url)
            assert page.locator('.item').count() == 51
            assert page.locator('#sources .source-grid').count() == 2
            assert 'Aucun inventaire' in page.locator('#notice').inner_text()
            page.locator('#ankiFile').set_input_files({
                'name': 'synthetic.apkg', 'mimeType': 'application/octet-stream', 'buffer': package_bytes()})
            page.wait_for_function('EDN_AUDIT_TEST.getState().inventory !== null')
            inventory = page.evaluate('EDN_AUDIT_TEST.getState().inventory')
            assert len(inventory['notes']) == 1 and inventory['notes'][0]['nid'] == '100'
            item_id = page.evaluate('EDN_AUDIT_TEST.getState().selectedId')
            status = lambda: page.evaluate('(id)=>EDN_AUDIT_TEST.status(id)', item_id)
            assert status() == 'suggested'
            print('PASS seed counts; local APKG import; numeric matching remains unconfirmed')
            page.locator('.source-panel').evaluate('(e)=>e.open=true')
            source = page.locator('.source-grid').first
            source.get_by_label('URL officielle (à vérifier)').fill('https://official.example.org/reference')
            source.get_by_label('Édition / version contrôlée').fill('Version synthétique de test')
            source.get_by_label('Date/version de la source vérifiée').fill('2026-11-06 test')
            source.locator('input[type=checkbox]').check()
            page.locator('.note-row input[type=checkbox]').check()
            page.locator('#editor label.check').filter(has_text='J’ai confirmé la correspondance').locator('input').check()
            page.get_by_role('button', name='Ajouter un objectif à contrôler').click()
            objective = page.locator('.objective')
            objective.get_by_label('Objectif / connaissance attendue (préciser le rang)').fill('Rang A — objectif synthétique')
            objective.get_by_label('Page, section ou identifiant de l’objectif dans la source').fill('p. 12 § A')
            objective.get_by_label('Rang dans ce collège').select_option('A')
            objective.get_by_label('Repère du collège qui justifie le rang', exact=True).fill('Tableau A/B, p. 12')
            objective.get_by_label('Constat').select_option('conforme')
            objective.locator('select[multiple]').select_option(inventory['notes'][0]['key'])
            page.locator('#editor label.check').filter(has_text='J’ai listé et contrôlé tous les objectifs').locator('input').check()
            page.get_by_label('Relecteur', exact=True).fill('Test automatisé, données fictives')
            page.get_by_label('Chapitre / pages / sections contrôlées').fill('p. 12–20')
            page.get_by_label('Conclusion de cette relecture').select_option('verified')
            page.get_by_role('button', name='Enregistrer la relecture', exact=True).click()
            assert status() == 'verified'
            page.get_by_label('Bilan et méthode de recherche (obligatoire si non retrouvé)').fill('Deuxième relecture synthétique')
            page.get_by_role('button', name='Enregistrer la relecture', exact=True).click()
            assert status() == 'verified'
            assert len(page.evaluate('EDN_AUDIT_TEST.getState().review_history')) == 1
            print('PASS objective/source/note evidence gating; historical snapshots')
            source.get_by_label('URL officielle (à vérifier)').fill('https://official.example.org/reference-v2')
            assert status() == 'stale'
            assert not source.locator('input[type=checkbox]').is_checked()
            altered = json.loads(json.dumps(inventory))
            altered['bundle_sha256'] = 'e' * 64
            altered['notes'][0]['key'] = 'changed:100'
            altered['notes'][0]['sha256'] = 'f' * 64
            page.locator('#inventoryFile').set_input_files({
                'name': 'changed.json', 'mimeType': 'application/json', 'buffer': json.dumps(altered).encode()})
            assert status() == 'stale'
            page.get_by_role('button', name='Retirer cette ancienne association').click()
            page.locator('.note-row input[type=checkbox]').check()
            state = page.evaluate('EDN_AUDIT_TEST.getState()')
            review = state['reviews'][item_id]
            assert review['note_keys'] == ['changed:100']
            assert not review['mapping_confirmed'] and not review['full_scope']
            print('PASS source/inventory invalidation; unavailable associations removable')
            page.evaluate('(text)=>{const s=EDN_AUDIT_TEST.getState();s.reviews[s.selectedId].objectives[0].text=text;}', '\n  =SUM(1,1)')
            with page.expect_download() as download:
                page.get_by_role('button', name='Objectifs détaillés (CSV)').click()
            csv = Path(download.value.path()).read_text(encoding='utf-8-sig')
            assert '"\'\n  =SUM(1,1)"' in csv
            with page.expect_download() as download:
                page.get_by_role('button', name='Sauvegarder tout (JSON)').click()
            backup = Path(download.value.path()).read_bytes()
            page.on('dialog', lambda d: d.accept())
            page.locator('#backupFile').set_input_files({
                'name': 'backup.json', 'mimeType': 'application/json', 'buffer': backup})
            assert 'restaurée' in page.locator('#notice').inner_text()
            assert page.evaluate('EDN_AUDIT_TEST.getState().inventory.bundle_sha256') == 'e' * 64
            print('PASS objective CSV formula protection; full backup restore')
            quota_context = browser.new_context()
            quota_context.add_init_script("Object.defineProperty(Storage.prototype,'setItem',{value:function(){throw new DOMException('QuotaExceededError','QuotaExceededError')}})")
            quota = quota_context.new_page()
            quota.goto(url)
            quota.locator('#inventoryFile').set_input_files({
                'name': 'changed.json', 'mimeType': 'application/json', 'buffer': json.dumps(altered).encode()})
            assert quota.locator('#storageWarning').is_visible()
            assert 'seulement en mémoire' in quota.locator('#storageWarning').inner_text()
            assert 'notes importées' in quota.locator('#notice').inner_text()
            print('PASS quota failure leaves a persistent warning alongside import result')
            assert not errors, errors
            page.screenshot(path='/tmp/edn-ui-tested.png', full_page=True)
            page.set_viewport_size({'width': 390, 'height': 844})
            page.screenshot(path='/tmp/edn-mobile-tested.png', full_page=True)
            browser.close()
    finally:
        server.shutdown()
        server.server_close()


if __name__ == '__main__':
    main()
