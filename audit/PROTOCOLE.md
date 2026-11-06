# Protocole d'audit — Deck EDN - MEA ↔ référentiel CEP 9e (pneumologie)

Ce document fait foi. Tout agent (Codex, Claude) ou relecteur humain le suit **à la lettre**.
En cas de doute non couvert ici : ne pas improviser, écrire le doute dans le rapport final.

> ⚠️ **Le dépôt est public.** Ne jamais y verser le texte du référentiel CEP ni le contenu
> des cartes du deck. Seuls les fichiers d'audit (constats reformulés, faits, chiffres) sont
> versionnés. Le contrôle automatique refuse toute suite de 15 mots copiée du référentiel.

## Étape 0 — Préparer les sources (une fois par session)

```sh
pip install python-docx
python outils/apkg_distant.py "https://drive.usercontent.google.com/download?id=1ocZ1MyNf3tOJyXOpxEDUoBMjbwHZe5WG&export=download&confirm=t" collection.anki21
mkdir -p local && mv collection.anki21 local/
python outils/mea_extraire.py local/collection.anki21 --out local/mea/notes.csv
mkdir -p local/cep9-docx && (cd local/cep9-docx && xargs -n1 curl -sSLO < ../../references/cep9/urls.txt)
(cd local/cep9-docx && sha256sum -c ../../references/cep9/SHA256SUMS)
python outils/cep9_extraire.py local/cep9-docx --objectifs local/objectifs-recalcules.csv --texte local/cep9
diff references/cep9/objectifs.csv local/objectifs-recalcules.csv && echo "objectifs identiques"
sha256sum local/collection.anki21   # attendu : 3967ffd79dd1aa8f39e192c3409745d01188ad77c2ee0ee6fe5461eb77321625
```

**Conditions d'arrêt.** Si un téléchargement échoue, si une empreinte SHA-256 diffère, ou si
les objectifs recalculés diffèrent de `references/cep9/objectifs.csv` : **arrêter**, ne rien
auditer, signaler le problème. Ne jamais auditer de mémoire ou à partir d'une autre édition.

## Étape 1 — Lire l'item en entier

```sh
mkdir -p local/travail
python outils/comparer_item.py ITEM > local/travail/item-ITEM.txt
```

- Le fichier contient d'abord le contenu A/B de la 9e (rang C déjà retiré), puis **toutes**
  les notes du deck rattachées à l'item, regroupées par verso identique.
- Le lire **intégralement**, des deux côtés. Une recherche par mots-clés ne suffit pas.
- **Notes de pédiatrie** : exclues par défaut (elles relèvent du collège de pédiatrie). Si le
  titre de l'item CEP ou un de ses objectifs vise l'enfant (ex. 207 « chez l'enfant et chez
  l'adulte », 359 bis), les inclure : `python outils/comparer_item.py ITEM --exclure`.
- `359 bis` : les notes sont rangées sous 359 ; ne retenir que celles qui traitent du corps
  étranger. Fichiers : `item-359bis.csv`.

## Étape 2 — Juger chaque objectif officiel

Les objectifs sont dans `references/cep9/objectifs.csv` (identifiant `cep9:ITEM:NN`). Pour
chacun : repérer le contenu A/B de la 9e qui s'y rapporte, puis les notes qui le couvrent.

| statut | quand l'utiliser |
|---|---|
| `conforme` | tout le contenu A/B de l'objectif est présent et exact dans les notes citées |
| `partiel` | une partie du contenu A/B manque ; rien n'est contredit |
| `à mettre à jour` | une note contredit la 9e ou reprend une version dépassée (chiffre, seuil, classification, traitement, conduite à tenir) |
| `non retrouvé` | aucune note ne couvre l'objectif |
| `à vérifier dans Anki` | l'objectif dépend d'images ou de médias (« Contenu multimédia ») |
| `divergent (autre collège)` | la note qui diffère est rangée dans une autre matière (ex. INFECTIOLOGIE, CARDIOLOGIE) et suit vraisemblablement son propre collège : ne pas l'écraser, la signaler |

Plusieurs situations pour un même objectif : retenir la plus sévère
(`à mettre à jour` > `divergent` > `non retrouvé` > `partiel` > `à vérifier dans Anki` > `conforme`).

Règles :
1. **Rang C ignoré.** Ne jamais proposer de supprimer ni de suspendre une carte.
2. **Ce que le deck ajoute** (autre source, détail absent de la 9e) n'est pas une erreur. Le
   mentionner dans le constat ; une correction `signaler` seulement s'il contredit la 9e.
3. **Rien d'inventé.** Chaque affirmation sur la 9e doit se retrouver dans
   `local/cep9/item-ITEM.txt` ; indiquer la section dans `repere_cep9`. Si le texte est
   ambigu : statut le plus prudent et « à confirmer par un humain » dans le constat.
4. **Identifiants de notes** (`nid`) : les recopier depuis le fichier de l'étape 1, jamais de
   mémoire. Plusieurs nid séparés par des espaces.
5. **Reformuler.** Constats et propositions en phrases courtes, avec les faits et chiffres
   exacts, sans recopier de phrase du référentiel. `actuel` = court extrait de la note (une
   phrase au plus).
6. `constat` dit ce qui a été vérifié, même pour `conforme` (« A, B, C présents et exacts »).
7. `verifie_par` = nom de l'agent et du modèle ; `verifie_le` = date AAAA-MM-JJ ;
   `relu_par` et `relu_le` restent **vides** (réservés au relecteur humain).

## Étape 3 — Écrire les deux fichiers

`audit/pneumologie/item-ITEM.csv` — une ligne par objectif, colonnes exactes :

```
objectif_id,rang,rubrique,intitule,statut,notes_mea,constat,action,repere_cep9,verifie_par,verifie_le,relu_par,relu_le
```

`audit/pneumologie/item-ITEM-corrections.csv` — une ligne par modification :

```
ref,type,nid,objectif_id,rang,champ,actuel,propose,justification_cep9
```

- `ref` : `C1, C2…` (notes existantes), `N1, N2…` (nouvelles cartes).
- `type` : `modifier` (texte de remplacement complet de la partie concernée dans `propose`),
  `signaler` (écart à faire trancher, pas de modification imposée), `nouvelle`
  (`propose` = `Recto : … — Verso : …`, `nid` vide).
- Tout objectif `partiel`, `à mettre à jour`, `divergent` ou `non retrouvé` a au moins une
  ligne ici ; `non retrouvé` a au moins une carte `nouvelle`.

Modèles : `audit/pneumologie/item-204*.csv`, `item-205*.csv`, `item-360*.csv`.

## Étape 4 — Contrôler, puis valider

```sh
python outils/valider_audit.py ITEM
```

**0 erreur obligatoire.** Lire chaque avertissement : un nid « pas rangé sous l'item » est
admis s'il est justifié dans le constat. Ne jamais modifier `outils/`, `references/` ni
`audit/README.md` pour faire passer le contrôle : signaler le problème à la place.

Un commit par item : `Audit item ITEM (titre court)`, contenant **uniquement**
`audit/pneumologie/item-ITEM.csv` et `item-ITEM-corrections.csv`.

## Étape 5 — Rapport final

Pour chaque item : nombre d'objectifs par statut, les 3 écarts les plus importants, les
doutes laissés « à confirmer par un humain », et la sortie de `valider_audit.py`.
