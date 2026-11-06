/* Offline EDN review register. Imported Anki text is never rendered as HTML. */
'use strict';
(() => {
  const STORAGE = 'edn-audit-register-v1';
  const seed = window.EDN_SEED || {sources:[],items:[],scope:[]};
  const clone = x => JSON.parse(JSON.stringify(x));
  const RANK_POLICY = Object.freeze({version:'pneumo-neuro-ab-v1',specialties:['Pneumologie','Neurologie'],included_ranks:['A','B'],excluded_ranks:['C'],unknown_rank:'must_be_clarified',notes:'Retained; rank is assessed per objective and college, never per whole note.'});
  const initial = () => ({format:'edn-audit-backup',version:1,manifest:clone(seed),inventory:null,reviews:{},review_history:[],rank_policy:clone(RANK_POLICY),mapping:{},selectedId:seed.items[0]?.id || null});
  let state=initial(), storageOK=true;
  const $=id=>document.getElementById(id);
  const E=(tag, text, cls)=>{const e=document.createElement(tag);if(text!==undefined)e.textContent=String(text);if(cls)e.className=cls;return e;};
  const norm=x=>String(x??'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
  const num=x=>String(x??'').trim().toLowerCase().replace(/^0+(?=\d)/,'').replace(/\s+/g,' ').replace(/^(\d+)\s*(bis|ter)$/,'$1 $2');
  const safeURL=x=>{try{const u=new URL(x);return ['https:','http:'].includes(u.protocol)?u.href:null;}catch{return null;}};
  const date=()=>new Date().toISOString();
  let noteByKey=new Map(), numberIndex=new Map(), searchIndex=new Map();
  function notice(message,error=false){$('notice').textContent=message;$('notice').className='notice visible'+(error?' error':'');}
  function renderStorageWarning(){const host=$('storageWarning');host.style.display=storageOK?'none':'block';host.textContent='Sauvegarde automatique indisponible ou quota dépassé : les données actuelles sont seulement en mémoire. Exportez « Sauvegarder tout (JSON) » avant de fermer, recharger ou changer cette page. Une ancienne sauvegarde du navigateur peut subsister.';}
  function persist(){try{localStorage.setItem(STORAGE,JSON.stringify(state));storageOK=true;}catch{storageOK=false;}renderStorageWarning();}
  function indexNotes(){noteByKey=new Map();numberIndex=new Map();searchIndex=new Map();for(const n of state.inventory?.notes||[]){noteByKey.set(n.key,n);searchIndex.set(n.key,norm([n.nid,n.key,...n.tags,...n.decks,...n.fields.map(f=>f.text)].join(' ')));for(const v of new Set(n.item_candidates.map(num))){if(!numberIndex.has(v))numberIndex.set(v,[]);numberIndex.get(v).push(n);}}}
  const idOK=x=>typeof x==='string'&&/^[a-zA-Z0-9_.:-]+$/.test(x)&&!Object.prototype.hasOwnProperty.call(Object.prototype,x)&&x!=='prototype';
  const stringList=x=>Array.isArray(x)&&x.every(v=>typeof v==='string');
  function isManifest(v){return v&&Array.isArray(v.sources)&&v.sources.length>0&&Array.isArray(v.items)&&v.items.length>0&&v.sources.every(s=>s&&idOK(s.id)&&typeof s.specialty==='string'&&typeof s.title==='string'&&typeof s.sha256==='string'&&/^[a-f0-9]{64}$/i.test(s.sha256))&&v.items.every(i=>i&&idOK(i.id)&&typeof i.title==='string'&&(i.number===null||typeof i.number==='string')&&v.sources.some(s=>s.id===i.source_id))&&new Set(v.sources.map(s=>s.id)).size===v.sources.length&&new Set(v.items.map(i=>i.id)).size===v.items.length;}
  function isReview(r){return r&&stringList(r.note_keys)&&typeof r.reviewer==='string'&&typeof r.source_locator==='string'&&typeof r.comment==='string'&&Array.isArray(r.objectives)&&r.objectives.every(o=>o&&typeof o.text==='string'&&typeof o.locator==='string'&&stringList(o.note_keys)&&typeof o.verdict==='string'&&(o.rank_locator===undefined||typeof o.rank_locator==='string'))&&['partial','not_found','discrepancy','verified'].includes(r.outcome);}
  function isInventory(v){return v&&v.schema_version===1&&typeof v.bundle_sha256==='string'&&Array.isArray(v.notes)&&v.notes.every(n=>n&&typeof n.key==='string'&&typeof n.sha256==='string'&&Array.isArray(n.fields)&&n.fields.every(f=>f&&typeof f.text==='string')&&stringList(n.tags)&&stringList(n.decks)&&stringList(n.item_candidates))&&new Set(v.notes.map(n=>n.key)).size===v.notes.length;}
  function isBackup(v){return v&&v.format==='edn-audit-backup'&&v.version===1&&isManifest(v.manifest)&&v.reviews&&typeof v.reviews==='object'&&!Array.isArray(v.reviews)&&Object.entries(v.reviews).every(([k,r])=>idOK(k)&&isReview(r))&&v.mapping&&typeof v.mapping==='object'&&!Array.isArray(v.mapping)&&Object.entries(v.mapping).every(([k,m])=>idOK(k)&&m&&(m.number===null||typeof m.number==='string'))&&(!v.review_history||(Array.isArray(v.review_history)&&v.review_history.every(h=>h&&idOK(h.item_id)&&isReview(h.review))))&&(!v.inventory||isInventory(v.inventory));}
  try{const raw=localStorage.getItem(STORAGE);if(raw){const v=JSON.parse(raw);if(isBackup(v))state=v;else notice('La sauvegarde locale est incompatible. Le registre fourni a été chargé.',true);}}catch{storageOK=false;}
  indexNotes();
  const getItem=id=>state.manifest.items.find(i=>i.id===id);
  const getSource=item=>state.manifest.sources.find(s=>s.id===item.source_id)||{};
  const itemNumber=item=>state.mapping[item.id]?.number||item.number;
  const refSignature=item=>JSON.stringify({source:getSource(item),item:{...item,number:itemNumber(item)}});
  function policyFor(item){return ['pneumologie','neurologie'].includes(norm(getSource(item).specialty))?RANK_POLICY:null;}
  function policySignature(item){return policyFor(item)?RANK_POLICY.version+':'+norm(getSource(item).specialty):null;}
  function objectiveRank(o){return ['A','B','C'].includes(o?.rank)?o.rank:'unknown';}
  function objectiveScope(item,o){
    if(!policyFor(item))return 'included';
    const rank=objectiveRank(o);
    if(rank==='unknown'||!o.text?.trim()||!o.rank_locator?.trim())return 'unknown';
    return rank==='C'?'excluded':'included';
  }
  function objectiveConforme(item,o,r){return objectiveScope(item,o)==='included'&&!!(o.text?.trim()&&o.locator?.trim()&&o.verdict==='conforme'&&o.note_keys?.length&&o.note_keys.every(k=>noteByKey.has(k)&&r?.note_keys?.includes(k)));}
  function trackedNoteKeys(item,r){return policyFor(item)?[...new Set((r.objectives||[]).filter(o=>objectiveScope(item,o)==='included').flatMap(o=>o.note_keys||[]))]:r.note_keys;}
  function objectiveCounts(item,r=review(item)){
    const all=r?.objectives||[],included=all.filter(o=>objectiveScope(item,o)==='included');
    return {total:all.length,included:included.length,conforme:included.filter(o=>objectiveConforme(item,o,r)).length,excluded:all.filter(o=>objectiveScope(item,o)==='excluded').length,unknown:all.filter(o=>objectiveScope(item,o)==='unknown').length};
  }
  function rankScopeText(item,r){const c=objectiveCounts(item,r);return `${c.included} objectif(s) A/B attendus · ${c.conforme} conformes avec preuves · ${c.excluded} rang C exclus · ${c.unknown} rang(s) à clarifier`;}
  const labels={unreviewed:'Non analysé',suggested:'Repéré, à confirmer',not_found:'Non retrouvé',partial:'Couverture partielle',discrepancy:'Écart constaté',verified:'Vérifié sur cette version',stale:'Relecture à refaire'};
  function suggestions(item){const number=itemNumber(item);return number?(numberIndex.get(num(number))||[]):[];}
  function freshReview(item){return {note_keys:[],mapping_confirmed:false,reviewer:'',source_locator:'',comment:'',full_scope:false,objectives:[],outcome:'partial',reviewed_at:null,dirty:true};}
  function review(item){return state.reviews[item.id]||null;}
  function editReview(item){return state.reviews[item.id]||(state.reviews[item.id]=freshReview(item));}
  function validation(item,r){
    const s=getSource(item), errors=[];
    if(!state.inventory)errors.push('Importer un inventaire Anki.');
    if(state.inventory?.complete!==true)errors.push('L’inventaire importé n’est pas déclaré complet pour les fichiers analysés.');
    if(!safeURL(s.url))errors.push('Renseigner une URL officielle http(s) pour la source.');
    if(!String(s.edition||'').trim())errors.push('Renseigner l’édition contrôlée.');
    if(!String(s.verified_source_version||'').trim())errors.push('Renseigner la date/version de la source vérifiée.');
    if(s.current_confirmed!==true)errors.push('Confirmer l’édition actuelle auprès du collège dans le registre des sources.');
    if(!r?.mapping_confirmed)errors.push('Confirmer la correspondance entre le chapitre et les notes.');
    if(!r?.reviewer?.trim())errors.push('Renseigner le nom du relecteur.');
    if(!r?.source_locator?.trim())errors.push('Indiquer les pages ou sections du chapitre contrôlé.');
    if(!r?.full_scope)errors.push('Confirmer que la liste des objectifs couvre tout le chapitre et les rangs attendus.');
    if(!policyFor(item)&&!r?.note_keys?.length)errors.push('Associer au moins une note Anki.');
    if(!policyFor(item)&&r?.note_keys?.some(k=>!noteByKey.has(k)))errors.push('Certaines notes associées ne figurent plus dans cet inventaire.');
    if(!r?.objectives?.length)errors.push('Lister les objectifs attendus et leurs preuves.');
    if(policyFor(item)&&objectiveCounts(item,r).included===0)errors.push('Au moins un objectif de rang A ou B, justifié dans ce collège, est nécessaire : un périmètre uniquement C ne peut pas être validé.');
    for(const [i,o] of (r?.objectives||[]).entries()){
      const scope=objectiveScope(item,o);
      if(scope==='unknown'){errors.push(`Objectif ${i+1} : le rang doit être A, B ou C et justifié par un repère du collège ; un rang inconnu ne peut pas être ignoré.`);continue;}
      if(scope==='excluded')continue;
      if(!objectiveConforme(item,o,r))errors.push(`Objectif ${i+1} : il faut un intitulé, un repère source, un verdict conforme et des notes associées valides.`);
    }
    if(r?.outcome!=='verified')errors.push(policyFor(item)?'Choisir « Tout le périmètre A/B contrôlé est conforme ».':'Choisir « Tout le périmètre contrôlé est conforme ».');
    return errors;
  }
  function stale(item,r){return !!(r?.reviewed_at&&(r.bundle_sha256!==state.inventory?.bundle_sha256||r.reference_signature!==refSignature(item)||(policyFor(item)&&r.rank_policy_signature!==policySignature(item))||Object.entries(r.note_hashes||{}).some(([k,h])=>noteByKey.get(k)?.sha256!==h)));}
  function status(item){const r=review(item);if(stale(item,r))return 'stale';if(r){if(r.outcome==='discrepancy'||r.objectives?.some(o=>objectiveScope(item,o)==='included'&&o.verdict==='ecart'))return 'discrepancy';if(r.reviewed_at&&!r.dirty&&r.outcome==='verified'&&!validation(item,r).length)return 'verified';if(r.reviewed_at&&!r.dirty&&r.outcome==='not_found')return 'not_found';if(r.note_keys?.length||r.objectives?.length||r.reviewed_at)return 'partial';}return suggestions(item).length?'suggested':'unreviewed';}
  function touch(item){const r=editReview(item);r.dirty=true;persist();updateSummary();renderList();}
  function field(labelText,value,onInput,{type='text',placeholder=''}={}){const l=E('label',labelText),i=E(type==='textarea'?'textarea':'input');if(type!=='textarea')i.type=type;i.value=value||'';i.placeholder=placeholder;i.addEventListener('input',()=>onInput(i.value));l.append(i);return l;}
  function check(text,value,onChange){const l=E('label',undefined,'check'),i=E('input');i.type='checkbox';i.checked=!!value;i.addEventListener('change',()=>onChange(i.checked));l.append(i,E('span',text));return l;}
  function btn(text,fn,cls=''){const b=E('button',text,cls);b.type='button';b.addEventListener('click',fn);return b;}
  function sourceLink(source){const url=safeURL(source.url);if(!url)return E('span','URL officielle à renseigner','muted');const a=E('a','Ouvrir la source officielle ↗');a.href=url;a.target='_blank';a.rel='noopener noreferrer';return a;}
  function updateSummary(){const items=state.manifest.items, verified=items.filter(i=>status(i)==='verified').length, staleCount=items.filter(i=>status(i)==='stale').length;const parts=[[items.length,'chapitres dans les listes fournies'],[state.inventory?state.inventory.notes.length:'—','notes Anki importées'],[verified,'chapitres relus et documentés'],[staleCount,'relectures à refaire']];$('inventorySummary').replaceChildren(...parts.map(([v,t])=>{const e=E('div',undefined,'metric');e.append(E('strong',v),E('span',t));return e;}));}
  function renderSources(){
    const host=$('sources');host.replaceChildren();
    for(const s of state.manifest.sources){const row=E('section',undefined,'source-grid'),info=E('div'),forms=E('div',undefined,'source-fields');info.append(E('h3',s.specialty+' · '+s.title),E('p',s.limitation||''),E('p','Date annoncée : '+(s.declared_updated_at||'indéterminée')),E('p','Empreinte du texte fourni : '+(s.sha256||'non fournie'),'note-meta'));if(['pneumologie','neurologie'].includes(norm(s.specialty)))info.append(E('p','Périmètre de contrôle : rangs A et B uniquement. Le rang C reste conservé, hors calcul ; tout rang non justifié reste à clarifier. Aucune carte n’est supprimée.','callout'));
      const link=E('div');link.append(sourceLink(s));info.append(link);
      const changed=()=>{s.current_confirmed=false;const checkbox=forms.querySelector('input[type=checkbox]');if(checkbox)checkbox.checked=false;persist();updateSummary();renderList();};
      forms.append(field('URL officielle (à vérifier)',s.url,v=>{s.url=v;changed();link.replaceChildren(sourceLink(s));}),field('Édition / version contrôlée',s.edition,v=>{s.edition=v;changed();}),field('Date/version de la source vérifiée',s.verified_source_version,v=>{s.verified_source_version=v;changed();}),check('J’ai vérifié auprès du collège que cette édition est l’édition actuelle.',s.current_confirmed,v=>{s.current_confirmed=v;s.current_confirmed_at=v?date():null;persist();updateSummary();renderList();if(state.selectedId)renderEditor();}));
      row.append(info,forms);host.append(row);
    }
    const scope=$('scope');scope.replaceChildren(E('h3','Périmètre et sources encore manquantes'));const chips=E('div',undefined,'scope-list');for(const s of state.manifest.scope||[])chips.append(E('span',s.specialty+' — '+s.status,'scope-chip'));scope.append(chips);
    if(state.manifest.research_tasks?.length){const tasks=E('div');tasks.append(E('h3','Sources à rechercher et document à lire'));for(const t of state.manifest.research_tasks){const entry=E('section',undefined,'source-grid'),text=E('div');text.append(E('h4',t.title),E('p',t.status),E('p',t.evidence_required,'muted'));const url=safeURL(t.url);if(url){const a=E('a',t.link_label||'Ouvrir la piste');a.href=url;a.target='_blank';a.rel='noopener noreferrer';entry.append(text,a);}else entry.append(text);tasks.append(entry);}scope.append(tasks);}

  }
  function renderFilters(){const sel=$('specialtyFilter');const current=sel.value;sel.replaceChildren(new Option('Toutes',''));for(const s of [...new Set(state.manifest.sources.map(s=>s.specialty))])sel.add(new Option(s,s));sel.value=current;}
  function renderList(){
    const query=norm($('itemSearch').value),spec=$('specialtyFilter').value,st=$('statusFilter').value;
    const rows=state.manifest.items.filter(i=>(!spec||getSource(i).specialty===spec)&&(!query||norm([itemNumber(i),i.title,getSource(i).specialty].join(' ')).includes(query))&&(!st||status(i)===st));
    $('itemCount').textContent=`${rows.length} / ${state.manifest.items.length} chapitres`;
    const list=$('itemList');list.replaceChildren();for(const i of rows){const s=status(i),b=btn('',()=>{state.selectedId=i.id;persist();renderList();renderEditor();},'item'+(state.selectedId===i.id?' selected':''));b.append(E('span',itemNumber(i)?'ITEM '+itemNumber(i):'NUMÉRO À CONFIRMER','number'),E('strong',i.title),E('span',labels[s],'badge '+s));list.append(b);}if(!rows.length)list.append(E('div','Aucun chapitre pour ces filtres.','empty'));
  }
  function renderEditor(){
    const host=$('editor'),item=getItem(state.selectedId);host.replaceChildren();if(!item){host.append(E('p','Sélectionnez un chapitre.'));return;}
    const s=getSource(item),r=editReview(item),st=status(item);host.append(E('p',getSource(item).specialty+' · '+(itemNumber(item)?'Item '+itemNumber(item):'Numéro national non confirmé'),'eyebrow'),E('h2',item.title));const sub=E('div',undefined,'subline');sub.append(E('span',labels[st],'badge '+st),sourceLink(s));host.append(sub);
    if(policyFor(item))host.append(E('p','Dans ce collège, seules les informations de rang A et B entrent dans le contrôle. Les informations C sont conservées hors calcul. Une note partagée reste disponible, même si elle est C ici et A/B ailleurs. Les rangs sont confirmés dans la source, jamais déduits automatiquement des tags.','callout'));
    if(st==='stale')host.append(E('p','L’inventaire, la source, la correspondance ou la règle de contrôle a changé depuis la relecture. Les preuves restent visibles ; elles doivent être contrôlées à nouveau.','callout invalid'));
    if(!state.inventory)host.append(E('p','Aucun paquet Anki n’a encore été analysé ici. Les listes de chapitres seules ne permettent pas de conclure à une absence ou à une mise à jour.','callout'));
    if(state.inventory?.warnings?.length){const warnings=E('details');warnings.append(E('summary',`${state.inventory.warnings.length} avertissement(s) d’import`));for(const w of state.inventory.warnings)warnings.append(E('p',typeof w==='string'?w:JSON.stringify(w),'muted'));host.append(warnings);}
    if(item.number_status==='unknown'||state.mapping[item.id]){const mapping=field('Numéro national (optionnel ; confirmer sur une source officielle)',itemNumber(item),v=>{state.mapping[item.id]={number:v.trim()||null};touch(item);}, {placeholder:'Ne pas déduire le numéro du titre'});host.append(mapping);}
    host.append(E('h3','1 · Associer les notes à ce chapitre'));
    const lead=E('p','Les numéros détectés dans les tags ou paquets sont des pistes. Sélectionnez les notes puis confirmez vous-même la correspondance.','muted');host.append(lead);
    const search=field('Rechercher dans tout l’inventaire', '',()=>renderNotes(),{type:'search',placeholder:'Titre, texte, tag, numéro ou identifiant de note'});const searchInput=search.querySelector('input');host.append(search);
    const selectedOnly=check('Afficher uniquement les notes associées',false,()=>renderNotes());host.append(selectedOnly);
    const noteCount=E('div','','muted'),noteList=E('div',undefined,'note-list'),missingList=E('div');host.append(noteCount,noteList,missingList);
    function renderMissing(){missingList.replaceChildren();const keys=r.note_keys.filter(k=>!noteByKey.has(k));if(!keys.length)return;missingList.append(E('p','Associations issues d’un ancien inventaire : ces notes ne sont plus accessibles dans le fichier chargé. Réassociez les objectifs aux notes actuelles avant de valider.','callout invalid'));for(const key of keys){const row=E('div',undefined,'pill-row');row.append(E('span',key,'note-meta'),btn('Retirer cette ancienne association',()=>{r.note_keys=r.note_keys.filter(k=>k!==key);for(const o of r.objectives)o.note_keys=o.note_keys.filter(k=>k!==key);r.mapping_confirmed=false;r.full_scope=false;touch(item);renderEditor();},'small'));missingList.append(row);}}
    let noteLimit=80;
    function renderNotes(){const query=norm(searchInput.value),assignedOnly=selectedOnly.querySelector('input').checked;const all=state.inventory?.notes||[];const hints=new Set(suggestions(item).map(n=>n.key));const sorted=all.filter(n=>(!assignedOnly||r.note_keys.includes(n.key))&&(!query||searchIndex.get(n.key).includes(query))).sort((a,b)=>(Number(r.note_keys.includes(b.key))-Number(r.note_keys.includes(a.key)))||(Number(hints.has(b.key))-Number(hints.has(a.key))));
      noteList.replaceChildren();noteCount.textContent=`${r.note_keys.length} note(s) associée(s) · ${sorted.length} résultat(s)${query||assignedOnly?'':' ; les correspondances de numéro sont affichées en premier'}`;
      for(const n of sorted.slice(0,noteLimit)){const row=E('div',undefined,'note-row'),preview=(n.fields.map(f=>f.text).join(' ').replace(/\s+/g,' ')).slice(0,180);const tick=check('Note '+n.nid+(hints.has(n.key)?' · numéro repéré':''),r.note_keys.includes(n.key),checked=>{r.note_keys=checked?[...new Set([...r.note_keys,n.key])]:r.note_keys.filter(k=>k!==n.key);touch(item);renderObjectiveNotes();updateRankSummary();noteCount.textContent=`${r.note_keys.length} note(s) associée(s) · ${sorted.length} résultat(s)`;});row.append(tick,E('span',preview,'note-preview'));const detail=E('details');detail.append(E('summary','Lire le contenu et les identifiants'),E('div',`Clé : ${n.key} · Paquets : ${n.decks.join(' ; ')} · Tags : ${n.tags.join(' ')}`,'note-meta'));if(/^\d+$/.test(String(n.nid)))detail.append(btn('Copier la recherche Anki nid:'+n.nid,()=>copyText('nid:'+n.nid),'small'));for(const f of n.fields){const div=E('div',undefined,'note-field');div.append(E('b',f.name||'Champ'),E('span',f.text));detail.append(div);}row.append(detail);noteList.append(row);}
      if(sorted.length>noteLimit)noteList.append(btn('Afficher 80 notes supplémentaires',()=>{noteLimit+=80;renderNotes();},'small'));
      if(!sorted.length)noteList.append(E('div',all.length?'Aucune note ne correspond à cette recherche. Ce résultat ne prouve pas l’absence du chapitre.':'Importez un inventaire pour consulter les notes.','empty'));
    }
    host.append(check('J’ai confirmé la correspondance de ces notes avec ce chapitre (et sa numérotation, si renseignée).',r.mapping_confirmed,v=>{r.mapping_confirmed=v;touch(item);}));
    host.append(E('h3','2 · Comparer les objectifs et le contenu'));
    host.append(E('p','Recopiez les objectifs attendus depuis la source : rangs A/B, diagnostics, traitements, seuils et algorithmes pertinents. Pour chaque objectif, indiquez la page/section et les notes qui le couvrent. Un échantillon reste une couverture partielle.','muted'));
    const rankSummary=E('p',undefined,'callout'),objectives=E('div');
    function updateRankSummary(){rankSummary.textContent=rankScopeText(item,r);rankSummary.hidden=!policyFor(item);for(const indicator of objectives.querySelectorAll('[data-rank-scope]')){const scope=objectiveScope(item,r.objectives[Number(indicator.dataset.rankScope)]);indicator.className='callout'+(scope==='unknown'?' invalid':'');indicator.textContent=scope==='excluded'?'Rang C justifié : objectif conservé dans le registre et les exports, hors couverture et validation A/B. Aucune note ni carte n’est supprimée.':scope==='unknown'?'Rang à clarifier ou à justifier dans la source : cet objectif ne peut pas être écarté du contrôle.':'Rang A/B justifié : cet objectif entre dans le contrôle et doit être couvert par des notes conformes.';}}
    host.append(rankSummary,objectives);updateRankSummary();
    function renderObjectiveNotes(){for(const select of objectives.querySelectorAll('select[data-objective]')){const idx=Number(select.dataset.objective),o=r.objectives[idx];select.replaceChildren();for(const k of r.note_keys){const n=noteByKey.get(k);if(!n)continue;const opt=new Option(`Note ${n.nid} · ${n.fields[0]?.text?.slice(0,70)||n.key}`,k);opt.selected=o.note_keys.includes(k);select.add(opt);}for(const k of o.note_keys.filter(k=>!r.note_keys.includes(k))){const opt=new Option('⚠ Note retirée : '+k,k);opt.selected=true;select.add(opt);}}}
    function renderObjectives(){
      objectives.replaceChildren();
      for(const [index,o] of r.objectives.entries()){
        const box=E('section',undefined,'objective'),top=E('div',undefined,'objective-top');
        top.append(E('h4','Objectif '+(index+1)),btn('Retirer',()=>{r.objectives.splice(index,1);touch(item);renderObjectives();},'small danger'));
        box.append(top,field('Objectif / connaissance attendue (préciser le rang)',o.text,v=>{o.text=v;touch(item);updateRankSummary();},{type:'textarea'}),field('Page, section ou identifiant de l’objectif dans la source',o.locator,v=>{o.locator=v;touch(item);updateRankSummary();}));
        if(policyFor(item)){
          const rankFields=E('div',undefined,'two-cols'),rankLabel=E('label','Rang dans ce collège'),rank=E('select');
          for(const [value,text] of [['unknown','À clarifier'],['A','A — inclus'],['B','B — inclus'],['C','C — conservé, hors calcul']])rank.add(new Option(text,value));
          rank.value=objectiveRank(o);rank.addEventListener('change',()=>{o.rank=rank.value;touch(item);renderObjectives();});rankLabel.append(rank);
          rankFields.append(rankLabel,field('Repère du collège qui justifie le rang',o.rank_locator,v=>{o.rank_locator=v;touch(item);updateRankSummary();}));box.append(rankFields);
          const indicator=E('p');indicator.dataset.rankScope=index;box.append(indicator);
        }
        const columns=E('div',undefined,'two-cols'),verdictLabel=E('label','Constat'),verdict=E('select');
        for(const [v,t] of [['a_verifier','À vérifier'],['conforme','Conforme au contenu de la source'],['manquant','Couverture manquante'],['ecart','Écart de contenu constaté']])verdict.add(new Option(t,v));
        verdict.value=o.verdict;verdict.addEventListener('change',()=>{o.verdict=verdict.value;touch(item);updateRankSummary();});verdictLabel.append(verdict);
        const notesLabel=E('label','Notes qui couvrent cet objectif'),select=E('select');select.multiple=true;select.dataset.objective=index;
        select.addEventListener('change',()=>{o.note_keys=[...select.selectedOptions].map(o=>o.value);touch(item);updateRankSummary();});notesLabel.append(select,E('div','Sélection multiple : Ctrl/Cmd + clic. Associez les notes à l’étape 1.','muted'));
        columns.append(verdictLabel,notesLabel);box.append(columns,field('Justification / écart / contrôle effectué',o.comment,v=>{o.comment=v;touch(item);},{type:'textarea'}));objectives.append(box);
      }
      if(!r.objectives.length)objectives.append(E('p','Aucun objectif documenté. La couverture complète ne peut pas être validée.','muted'));
      renderObjectiveNotes();updateRankSummary();
    }
    host.append(btn('Ajouter un objectif à contrôler',()=>{r.objectives.push({text:'',locator:'',rank:'unknown',rank_locator:'',note_keys:[],verdict:'a_verifier',comment:''});touch(item);renderObjectives();}));
    host.append(check('J’ai listé et contrôlé tous les objectifs du chapitre dans le périmètre attendu (A/B en pneumologie et neurologie), et justifié chaque rang C exclu. Je n’ai pas vérifié seulement un échantillon.',r.full_scope,v=>{r.full_scope=v;touch(item);}));
    host.append(E('h3','3 · Documenter la relecture'));
    const fields=E('div',undefined,'two-cols');fields.append(field('Relecteur',r.reviewer,v=>{r.reviewer=v;touch(item);}),field('Chapitre / pages / sections contrôlées',r.source_locator,v=>{r.source_locator=v;touch(item);}));host.append(fields,field('Bilan et méthode de recherche (obligatoire si non retrouvé)',r.comment,v=>{r.comment=v;touch(item);},{type:'textarea'}));
    const outcomeLabel=E('label','Conclusion de cette relecture'),outcome=E('select');for(const [v,t] of [['partial','Couverture partielle / relecture en cours'],['not_found','Non retrouvé après recherche (absence non prouvée)'],['discrepancy','Écart de contenu constaté'],['verified','Tout le périmètre contrôlé est conforme']])outcome.add(new Option(policyFor(item)&&v==='discrepancy'?'Écart de contenu A/B constaté':policyFor(item)&&v==='verified'?'Tout le périmètre A/B contrôlé est conforme':t,v));outcome.value=r.outcome;outcome.addEventListener('change',()=>{r.outcome=outcome.value;touch(item);showIssues();});outcomeLabel.append(outcome);host.append(outcomeLabel);
    const issues=E('div');host.append(issues);
    function showIssues(){issues.replaceChildren();if(r.outcome==='verified'){const errors=validation(item,r);if(errors.length){issues.append(E('p','Pour pouvoir enregistrer cette conclusion :','muted'));const ul=E('ul',undefined,'issues');for(const e of errors)ul.append(E('li',e));issues.append(ul);}}}
    const save=E('div',undefined,'save-row');save.append(btn('Enregistrer la relecture',()=>{if(r.outcome==='verified'){const errors=validation(item,r);if(errors.length){showIssues();notice('Relecture conservée en brouillon. La validation complète nécessite les preuves indiquées.',true);return;}}if(!r.reviewer.trim()||!r.source_locator.trim()){notice('Pour enregistrer une relecture, renseignez le relecteur et le repère source. Le brouillon est conservé.',true);return;}if(r.outcome==='not_found'&&!state.inventory){notice('Importez un inventaire avant de documenter un chapitre non retrouvé.',true);return;}if(r.outcome==='not_found'&&!r.comment.trim()){notice('Documentez les recherches effectuées avant de conclure « non retrouvé ».',true);return;}if(r.saved_snapshot){state.review_history=state.review_history||[];state.review_history.push({item_id:item.id,saved_at:date(),review:clone(r.saved_snapshot)});}r.reviewed_at=date();r.bundle_sha256=state.inventory?.bundle_sha256||null;r.reference_signature=refSignature(item);r.rank_policy_signature=policySignature(item);r.note_hashes=Object.fromEntries(trackedNoteKeys(item,r).map(k=>[k,noteByKey.get(k)?.sha256||null]));r.dirty=false;r.saved_snapshot=clone(Object.fromEntries(Object.entries(r).filter(([k])=>k!=='saved_snapshot')));persist();updateSummary();renderList();renderEditor();notice(storageOK?'Relecture enregistrée. Exportez une sauvegarde JSON pour conserver et partager les preuves.':'Relecture conservée uniquement en mémoire. Le quota du navigateur est dépassé : exportez une sauvegarde JSON avant de fermer cette page.');},'primary'));save.append(E('span','Les modifications sont conservées comme brouillon dans ce navigateur.','muted'));host.append(save);
    if(r.reviewed_at)host.append(E('div',`Dernier enregistrement : ${new Date(r.reviewed_at).toLocaleString('fr-FR')} · Relecteur : ${r.reviewer}\nInventaire : ${r.bundle_sha256||'aucun'}\nSource et correspondance : conservées dans la sauvegarde JSON.`,'audit-stamp'));
    const history=(state.review_history||[]).filter(h=>h.item_id===item.id);if(history.length)host.append(E('p',`${history.length} relecture(s) antérieure(s) conservée(s) avec leurs empreintes dans les exports JSON.`,'muted'));
    renderNotes();renderObjectives();renderMissing();showIssues();
  }
  async function copyText(t){try{await navigator.clipboard.writeText(t);notice('Recherche copiée : '+t);}catch{notice('À copier dans le navigateur Anki : '+t);}}
  function download(filename,data,mime='application/json'){const blob=new Blob([data],{type:mime}),url=URL.createObjectURL(blob),a=E('a');a.href=url;a.download=filename;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),3000);}
  function safeCell(v){let t=String(v??'');if(/^[\s\uFEFF]*[=+\-@]/.test(t)||/^[\t\r\n]/.test(t))t="'"+t;return '"'+t.replace(/"/g,'""')+'"';}
  function exportCSV(){
    const header=['specialite','item','titre','statut','edition','source_url','edition_actuelle_confirmee','notes_associees','objectifs_documentes','objectifs_conformes','objectifs_total_registre','objectifs_dans_perimetre','objectifs_rang_c_exclus','objectifs_rang_inconnu','politique_rangs','relecteur','date_relecture','repere_source','bilan','inventaire_sha256','relecture_invalidee'];
    const rows=state.manifest.items.map(i=>{const r=review(i)||{},s=getSource(i),c=objectiveCounts(i,r);return [s.specialty,itemNumber(i),i.title,labels[status(i)],s.edition,s.url,s.current_confirmed===true?'oui':'non',(r.note_keys||[]).join(' ; '),c.included,c.conforme,c.total,c.included,c.excluded,c.unknown,policySignature(i)||'tous_objectifs',r.reviewer,r.reviewed_at,r.source_locator,r.comment,state.inventory?.bundle_sha256||'',stale(i,r)?'oui':'non'];});
    download('registre-edn.csv','\uFEFF'+[header,...rows].map(row=>row.map(safeCell).join(';')).join('\r\n'),'text/csv;charset=utf-8');
  }
  async function readJSON(input,callback){const f=input.files?.[0];if(!f)return;try{const text=await f.text();const v=JSON.parse(text);callback(v);}catch(e){notice('Import impossible : '+e.message,true);}input.value='';}
  function acceptInventory(v){if(!isInventory(v))throw new Error('inventaire JSON incompatible ou identifiants de note dupliqués. Utilisez l’outil d’import fourni.');const replacing=state.inventory&&state.inventory.bundle_sha256!==v.bundle_sha256;state.inventory=v;indexNotes();persist();renderAll();notice(`${v.notes.length} notes importées. ${replacing?'Cet import remplace l’inventaire précédent : les relectures concernées sont à refaire. Pour réunir plusieurs fichiers, utilisez la commande d’import avec tous les fichiers.':'Les correspondances proposées doivent être confirmées.'}`);}
  $('inventoryFile').addEventListener('change',()=>readJSON($('inventoryFile'),acceptInventory));
  $('manifestFile').addEventListener('change',()=>readJSON($('manifestFile'),v=>{if(!isManifest(v))throw new Error('référentiel incompatible : sources et items non vides, identifiants uniques, liens item/source valides et empreintes SHA-256 sont requis.');if(!confirm('Charger ce référentiel remplace la liste des chapitres. Les relectures restent conservées et celles dont la source a changé seront à refaire. Continuer ?'))return;state.manifest=v;if(!getItem(state.selectedId))state.selectedId=v.items[0].id;persist();renderAll();notice('Référentiel chargé. Les anciennes relectures sont conservées dans la sauvegarde, y compris pour les chapitres retirés.');}));
  $('ankiFile').addEventListener('change',async()=>{const input=$('ankiFile'),f=input.files?.[0];if(!f)return;if(location.protocol==='file:'){notice('L’import direct Anki nécessite le lanceur local : depuis le dossier du système, lancez « python lancer.py ». En ouverture directe, chargez un inventaire JSON produit par l’outil.',true);input.value='';return;}if(state.inventory&&!confirm('Cet import remplace l’inventaire chargé. Pour auditer plusieurs fichiers ensemble, utilisez la commande d’import avec tous les fichiers. Continuer ?')){input.value='';return;}notice('Analyse du fichier Anki en cours, localement…');try{const response=await fetch('/api/import?filename='+encodeURIComponent(f.name),{method:'POST',headers:{'Content-Type':'application/octet-stream'},body:await f.arrayBuffer()});const data=await response.json();if(!response.ok)throw new Error(data.error||'échec de l’import');acceptInventory(data);}catch(e){notice('Import Anki impossible : '+e.message,true);}input.value='';});
  $('backupFile').addEventListener('change',()=>readJSON($('backupFile'),v=>{if(!isBackup(v))throw new Error('format de sauvegarde incompatible.');if(!confirm('Restaurer cette sauvegarde remplacera les données de ce navigateur. Exportez d’abord vos données actuelles si nécessaire. Continuer ?'))return;state=v;indexNotes();persist();renderAll();notice('Sauvegarde restaurée. Les empreintes et les preuves restent contrôlables.');}));
  $('exportBackup').addEventListener('click',()=>download('sauvegarde-edn-'+new Date().toISOString().slice(0,10)+'.json',JSON.stringify({...state,rank_policy:clone(RANK_POLICY),exported_at:date()},null,2)));
  $('exportCSV').addEventListener('click',exportCSV);
  $('exportObjectives').addEventListener('click',()=>{
    const header=['specialite','item','titre_chapitre','statut_chapitre','edition','source_url','source_sha256','objectif','rang_college','repere_source_rang','inclusion_controle','politique_rangs','repere_source_objectif','verdict_objectif','justification','notes_cles','notes_empreintes','notes_contenu','relecteur','date_relecture','inventaire_sha256','relecture_invalidee'];const rows=[];
    for(const item of state.manifest.items){const r=review(item),s=getSource(item);for(const o of r?.objectives||[]){const notes=o.note_keys.map(k=>noteByKey.get(k)).filter(Boolean);rows.push([s.specialty,itemNumber(item),item.title,labels[status(item)],s.edition,s.url,s.sha256,o.text,objectiveRank(o),o.rank_locator||'',objectiveScope(item,o),policySignature(item)||'tous_objectifs',o.locator,o.verdict,o.comment,o.note_keys.join(' ; '),notes.map(n=>n.key+'='+n.sha256).join(' ; '),notes.map(n=>'Note '+n.nid+' : '+n.fields.map(f=>f.name+': '+f.text).join(' | ')).join('\n\n'),r.reviewer,r.reviewed_at,state.inventory?.bundle_sha256,stale(item,r)?'oui':'non']);}}
    download('objectifs-edn.csv','\uFEFF'+[header,...rows].map(row=>row.map(safeCell).join(';')).join('\r\n'),'text/csv;charset=utf-8');
  });
  $('exportReviews').addEventListener('click',()=>download('relectures-edn.json',JSON.stringify({format:'edn-audit-reviews',version:1,rank_policy:clone(RANK_POLICY),exported_at:date(),bundle_sha256:state.inventory?.bundle_sha256||null,sources:state.manifest.sources,items:state.manifest.items,mapping:state.mapping,reviews:state.reviews,review_history:state.review_history||[]},null,2)));
  for(const id of ['specialtyFilter','statusFilter'])$(id).addEventListener('change',renderList);$('itemSearch').addEventListener('input',renderList);
  function renderAll(){renderSources();renderFilters();updateSummary();renderList();renderEditor();}
  renderAll();renderStorageWarning();if(!storageOK)notice('La sauvegarde locale du navigateur est indisponible. Utilisez régulièrement « Sauvegarder tout (JSON) ».',true);else if(!state.inventory)notice('Aucun inventaire Anki chargé : aucune conclusion sur la couverture ou l’actualité n’est encore établie.');
  window.EDN_AUDIT_TEST={getState:()=>state,status:id=>status(getItem(id)),validate:id=>validation(getItem(id),review(getItem(id))),policy:id=>policyFor(getItem(id)),policySignature:id=>policySignature(getItem(id)),counts:id=>objectiveCounts(getItem(id)),render:renderAll};
})();
