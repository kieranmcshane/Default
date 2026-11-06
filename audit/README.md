# Audit du Deck EDN - MEA contre les collèges

Méthode obligatoire : [PROTOCOLE.md](PROTOCOLE.md) · tâches : [TACHES.md](TACHES.md) · contrôle : `python outils/valider_audit.py` · avancement : `python outils/valider_audit.py --avancement`.

## Sources figées

| Élément | Version | Où la retrouver |
|---|---|---|
| Deck EDN - MEA (Mohamed El Amri) | `.apkg` du 2026-10-28 ; base `collection.anki21` sha256 `3967ffd79dd1aa8f39e192c3409745d01188ad77c2ee0ee6fe5461eb77321625` | Drive fourni ; extraction : `outils/apkg_distant.py` |
| Référentiel CEP pneumologie | 9e édition, fichiers DOCX mis en ligne en septembre 2026 | URL : `references/cep9/urls.txt` ; empreintes : `references/cep9/SHA256SUMS` |
| Objectifs officiels CEP 9e | 319 objectifs (197 A · 122 B) | `references/cep9/objectifs.csv` |

Les cartes de pneumologie du deck ont toutes été créées avant le 10 septembre 2026 :
elles reposent sur la 8e édition. L'audit consiste à les confronter à la 9e.

## Refaire la vérification (sans Claude)

```sh
pip install python-docx
# 1. Base du deck (15 Mo, sans les 1,6 Go de médias)
python outils/apkg_distant.py "https://drive.usercontent.google.com/download?id=1ocZ1MyNf3tOJyXOpxEDUoBMjbwHZe5WG&export=download&confirm=t" collection.anki21
python outils/mea_extraire.py collection.anki21 --out local/mea/notes.csv
# 2. Référentiel CEP 9e
mkdir -p local/cep9-docx && (cd local/cep9-docx && xargs -n1 curl -sSLO < ../../references/cep9/urls.txt)
(cd local/cep9-docx && sha256sum -c ../../references/cep9/SHA256SUMS)
python outils/cep9_extraire.py local/cep9-docx --objectifs references/cep9/objectifs.csv --texte local/cep9
```

`local/cep9/item-XXX.txt` contient le texte de l'item, chaque passage marqué `[A]`, `[B]`
ou `[C]` d'après la couleur du CEP (bleu = B, vert = C). `local/mea/notes.csv` contient
les notes du deck avec leurs numéros d'item. Ces deux fichiers restent en local.

Pour lire un item : `python outils/comparer_item.py 205` (contenu A/B du CEP puis notes MEA).

## Lire un audit d'item

`pneumologie/item-XXX.csv` : une ligne par objectif officiel A/B.

| statut | sens |
|---|---|
| conforme | le contenu A/B de la 9e est présent et exact dans les notes citées |
| partiel | une partie du contenu A/B manque |
| à mettre à jour | une note contredit la 9e ou lui manque un élément ajouté |
| non retrouvé | aucune note ne couvre l'objectif |
| à vérifier dans Anki | dépend d'images ou de médias non lisibles en texte |
| divergent (autre collège) | la note qui diffère est rangée dans une autre matière et suit son propre collège |

`pneumologie/item-XXX-corrections.csv` : modifications proposées, note par note
(`nid` = identifiant de la note dans Anki ; recherche `nid:1780590545604` dans le navigateur
d'Anki). `C` = modifier ou signaler une note existante, `N` = nouvelle carte.

Règles appliquées : rang C ignoré (aucune carte supprimée) ; les cartes pédiatriques
rattachées au même numéro (paquet `PEDIATRIE`) relèvent du collège de pédiatrie et ne sont
pas jugées contre le CEP. Les colonnes `relu_par` / `relu_le` sont à remplir par le
relecteur humain.

## Avancement — pneumologie (CEP 9e)

| Item | Notes MEA | Statut |
|---|---|---|
| 204 Toux | 105 (+ 31 pédiatrie hors périmètre) | audité : 5 conformes · 1 partiel · 3 à mettre à jour · 1 à vérifier dans Anki |
| 205 Hémoptysie | 71 | audité : 3 conformes · 1 partiel · 4 à mettre à jour |
| 360 Pneumothorax | 79 | audité : 3 conformes · 2 partiels · 4 à mettre à jour · 2 à vérifier dans Anki |
| 210 PID | 0 | non couvert (déclaré absent par l'auteur) |
| autres | | à faire |
