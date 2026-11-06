"""Optional rank-policy regression: python tests/ranks_browser.py.

Uses synthetic notes and sources. Playwright/Chromium are development-only.
This validates the audit software, not medical information or real Anki decks.
"""
from __future__ import annotations

import csv
import io
import json
import os
from pathlib import Path
import sys
import threading

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lancer


def inventory():
    return {
        'schema_version': 1, 'bundle_sha256': 'a' * 64,
        'complete': True, 'imported_at': '2026-11-06T00:00:00Z',
        'files': [{'name': 'synthetic.json', 'sha256': 'a' * 64, 'notes': 2, 'cards': 3}],
        'notes': [
            {'key': 'synthetic:101', 'nid': '101', 'guid': 'shared-guid',
             'tags': ['Item_075', 'Rang_C'], 'decks': ['Synthetic'],
             'fields': [{'name': 'Texte', 'text': 'Connaissance A/B et C partagée, exemple synthétique.'}],
             'sha256': 'b' * 64, 'card_count': 2, 'item_candidates': ['75'], 'source_file': 'synthetic.json'},
            {'key': 'synthetic:102', 'nid': '102', 'guid': 'other-guid',
             'tags': ['Rang_C'], 'decks': ['Synthetic'],
             'fields': [{'name': 'Texte', 'text': 'Autre carte conservée, exemple synthétique.'}],
             'sha256': 'c' * 64, 'card_count': 1, 'item_candidates': [], 'source_file': 'synthetic.json'}
        ], 'warnings': []}


def objective(rank='A', verdict='conforme', keys=None, title='Objectif synthétique'):
    return {'text': title, 'locator': 'Chapitre test, p. 12',
            'rank': rank, 'rank_locator': 'Tableau des rangs, p. 12',
            'verdict': verdict, 'note_keys': ['synthetic:101'] if keys is None else keys,
            'comment': 'Comparaison fictive pour tester le logiciel.'}


def prepare_review(page, item_id, objectives):
    page.evaluate('''({id, objectives}) => {
      const s=EDN_AUDIT_TEST.getState(); s.selectedId=id;
      const item=s.manifest.items.find(x=>x.id===id);
      const source=s.manifest.sources.find(x=>x.id===item.source_id);
      Object.assign(source, {url:'https://official.example.org/reference',
        edition:'Version synthétique', verified_source_version:'2026-11-06 test',
        current_confirmed:true, current_confirmed_at:'2026-11-06T00:00:00Z'});
      s.reviews[id]={note_keys:['synthetic:101'],mapping_confirmed:true,
        reviewer:'Test automatique, données fictives',source_locator:'Chapitre p. 12',
        comment:'Test de la règle, pas une vérification médicale.',full_scope:true,
        objectives, outcome:'verified',reviewed_at:null,dirty:true};
      EDN_AUDIT_TEST.render();
    }''', {'id': item_id, 'objectives': objectives})


def status(page, item_id):
    return page.evaluate('(id)=>EDN_AUDIT_TEST.status(id)', item_id)


def validation(page, item_id):
    return page.evaluate('(id)=>EDN_AUDIT_TEST.validate(id)', item_id)


def save(page):
    page.get_by_role('button', name='Enregistrer la relecture', exact=True).click()


def export_rows(page, button):
    with page.expect_download() as downloaded:
        page.locator(button).click()
    text=Path(downloaded.value.path()).read_text(encoding='utf-8-sig')
    return list(csv.DictReader(io.StringIO(text), delimiter=';'))


def main():
    from playwright.sync_api import sync_playwright
    server=lancer.HTTPServer(('127.0.0.1', 0), lancer.Handler)
    thread=threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path=os.environ.get('EDN_BROWSER_BINARY','/usr/bin/chromium'),
                                      headless=True,args=['--no-sandbox'])
            page=browser.new_page()
            errors=[]
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.goto(f'http://127.0.0.1:{server.server_port}/')
            page.locator('#inventoryFile').set_input_files({'name':'synthetic.json','mimeType':'application/json',
                                                          'buffer':json.dumps(inventory()).encode()})
            ids=page.evaluate('''() => {const s=EDN_AUDIT_TEST.getState();return {
                pneumo:s.manifest.items.find(i=>s.manifest.sources.find(x=>x.id===i.source_id).specialty==='Pneumologie').id,
                neuro:s.manifest.items.find(i=>s.manifest.sources.find(x=>x.id===i.source_id).specialty==='Neurologie').id};}''')
            before=page.evaluate('JSON.stringify(EDN_AUDIT_TEST.getState().inventory.notes)')

            # A/B objectives are counted; C objectives are retained without
            # requiring cards or content conformity. The same note may be mixed.
            objectives=[objective('A'), objective('B',title='Objectif B synthétique'),
                        objective('C','ecart',['synthetic:101'],title='Objectif C hors périmètre sur la même note'),
                        objective('C','manquant',[],title='Autre C sans carte')]
            prepare_review(page,ids['pneumo'],objectives)
            assert validation(page,ids['pneumo']) == [], validation(page,ids['pneumo'])
            assert page.evaluate('(id)=>EDN_AUDIT_TEST.counts(id)',ids['pneumo']) == {'included':2,'conforme':2,'excluded':2,'unknown':0,'total':4}
            save(page)
            assert status(page,ids['pneumo']) == 'verified'
            assert page.evaluate('EDN_AUDIT_TEST.getState().reviews[EDN_AUDIT_TEST.getState().selectedId].objectives.length') == 4
            assert page.evaluate('JSON.stringify(EDN_AUDIT_TEST.getState().inventory.notes)') == before
            print('PASS pneumologie A/B; C absent ou divergent exclu; objectifs et notes conservés')

            # A C classification belongs to a college objective, not a note.
            prepare_review(page,ids['neuro'],[objective('B')])
            assert validation(page,ids['neuro']) == []
            save(page)
            assert status(page,ids['neuro']) == 'verified'
            assert page.evaluate('EDN_AUDIT_TEST.getState().reviews[EDN_AUDIT_TEST.getState().selectedId].objectives[0].rank') == 'B'
            assert page.evaluate('JSON.stringify(EDN_AUDIT_TEST.getState().inventory.notes)') == before
            print('PASS neurologie B sur la même note, sans héritage du tag C ni suppression')

            # A missing association used only by a sourced C objective does not
            # block fresh A/B validation and is preserved for another scope.
            prepare_review(page,ids['pneumo'],[objective('A'),objective('C','ecart',['missing:c'])])
            page.evaluate('''() => {const s=EDN_AUDIT_TEST.getState();
              s.reviews[s.selectedId].note_keys.push('missing:c');EDN_AUDIT_TEST.render();}''')
            assert validation(page,ids['pneumo'])==[],validation(page,ids['pneumo'])
            save(page)
            assert status(page,ids['pneumo'])=='verified'
            saved=page.evaluate('EDN_AUDIT_TEST.getState().reviews[EDN_AUDIT_TEST.getState().selectedId]')
            assert 'missing:c' in saved['note_keys']
            assert saved['objectives'][1]['note_keys']==['missing:c']
            assert page.evaluate('JSON.stringify(EDN_AUDIT_TEST.getState().inventory.notes)')==before
            print('PASS association C indisponible conservée sans bloquer A/B ni invalider le nouveau contrôle')

            # Unknown or missing rank cannot silently drop an expected objective.
            for value in ['unknown', None]:
                o=objective('A')
                if value is None:
                    o.pop('rank')
                    o.pop('rank_locator')
                else:
                    o['rank']=value
                prepare_review(page,ids['pneumo'],[objective('A'),o])
                assert validation(page,ids['pneumo']), 'Unknown rank must block full validation'
                save(page)
                assert status(page,ids['pneumo']) != 'verified'
            prepare_review(page,ids['pneumo'],[objective('C','manquant',[])])
            assert validation(page,ids['pneumo']), 'All-C must not be presented as verified A/B coverage'
            save(page)
            assert status(page,ids['pneumo']) != 'verified'
            unsourced=objective('C','manquant',[])
            unsourced['rank_locator']=''
            prepare_review(page,ids['pneumo'],[objective('A'),unsourced])
            assert validation(page,ids['pneumo']), 'Unsourced C cannot silently leave the denominator'
            assert page.evaluate('(id)=>EDN_AUDIT_TEST.counts(id).unknown',ids['pneumo']) == 1
            print('PASS rang inconnu, ancien objectif et C non sourcé bloquants; zéro A/B non validable')

            # A/B missing or contradictory content is still blocking.
            for verdict in ['manquant','ecart']:
                prepare_review(page,ids['neuro'],[objective('B',verdict)])
                assert validation(page,ids['neuro'])
                save(page)
                assert status(page,ids['neuro']) != 'verified'
            print('PASS contenu A/B manquant ou divergent reste bloquant')

            # Existing saves must be revisited after enabling this policy.
            prepare_review(page,ids['pneumo'],[objective('A')])
            save(page)
            assert status(page,ids['pneumo']) == 'verified'
            page.evaluate('''() => {const s=EDN_AUDIT_TEST.getState();
                delete s.reviews[s.selectedId].rank_policy_signature;}''')
            assert status(page,ids['pneumo']) == 'stale'
            print('PASS anciennes validations sans signature de politique à refaire')

            # Other specialties keep the prior all-objectives rule.
            other_id='other:test'
            page.evaluate('''() => {const s=EDN_AUDIT_TEST.getState();
              s.manifest.sources.push({id:'other-source',specialty:'Orthopédie',title:'Source fictive',sha256:'d'.repeat(64)});
              s.manifest.items.push({id:'other:test',source_id:'other-source',number:null,title:'Chapitre fictif',number_status:'unknown'});
            }''')
            prepare_review(page,other_id,[objective('C','ecart')])
            assert validation(page,other_id)
            assert status(page,other_id)=='discrepancy'
            prepare_review(page,other_id,[objective('unknown')])
            assert validation(page,other_id)==[], validation(page,other_id)
            save(page)
            assert status(page,other_id)=='verified'
            print('PASS autres spécialités inchangées')

            # Fixture for inspectable exports: count only A/B in the chapter,
            # retain C and unknown rows in the detailed evidence export.
            prepare_review(page,ids['pneumo'],[objective('A'),objective('B','manquant'),
              objective('C','ecart',[]),objective('unknown')])
            chapter_rows=export_rows(page,'#exportCSV')
            detailed_rows=export_rows(page,'#exportObjectives')
            source_state=page.evaluate('''() => {const s=EDN_AUDIT_TEST.getState();
                const i=s.manifest.items.find(x=>x.id===s.selectedId);
                return {title:i.title,specialty:s.manifest.sources.find(x=>x.id===i.source_id).specialty};}''')
            chapter=next(row for row in chapter_rows if row['titre']==source_state['title'] and row['specialite']==source_state['specialty'])
            assert chapter['objectifs_documentes']=='2',chapter
            assert chapter['objectifs_total_registre']=='4',chapter
            assert chapter['objectifs_dans_perimetre']=='2',chapter
            assert chapter['objectifs_conformes']=='1',chapter
            assert chapter['objectifs_rang_c_exclus']=='1',chapter
            assert chapter['objectifs_rang_inconnu']=='1',chapter
            assert chapter['politique_rangs'],chapter
            detailed=[row for row in detailed_rows if row['titre_chapitre']==source_state['title'] and row['specialite']==source_state['specialty']]
            assert len(detailed)==4
            assert [(row['rang_college'],row['inclusion_controle']) for row in detailed] == [('A','included'),('B','included'),('C','excluded'),('unknown','unknown')],detailed
            assert all(row['repere_source_rang']=='Tableau des rangs, p. 12' for row in detailed)
            assert page.evaluate('JSON.stringify(EDN_AUDIT_TEST.getState().inventory.notes)')==before
            print('PASS CSV : couverture A/B uniquement, C exclu conservé et rang inconnu explicite')
            assert not errors,errors
            browser.close()
    finally:
        server.shutdown()
        server.server_close()


if __name__=='__main__':
    main()
