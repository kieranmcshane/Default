# Mise à jour des decks Anki EDN

Dépôt de travail commun pour vérifier que les decks Anki EDN couvrent les éditions
récentes des référentiels des collèges d'enseignants, et le rester.

## Objectif

- Vérifier que **tous les items** des éditions récentes des collèges sont **présents**
  dans les decks Anki utilisés, et **à jour** : un item peut être présent mais
  correspondre à une ancienne édition.
- La vérification doit pouvoir être **refaite par un humain**, sans dépendre d'un
  agent IA. Chaque validation garde sa trace : source, édition, référence,
  écart constaté, relecteur, date.

## Périmètre

| Collège | Statut |
|---|---|
| Pneumologie | 22 entrées recensées ; contrôle A/B implémenté, cartes réelles non auditées |
| Neurologie | 29 chapitres recensés ; numéros à confirmer, contrôle A/B implémenté |
| Orthopédie | à recenser |
| Cancérologie | à recenser |
| Néphrologie | à recenser |
| Santé publique | à recenser |

Les éditions récentes sont à chercher sur les sites des collèges : sans elles, on
ne connaît pas les derniers items.

## Règles de vérification

1. **Seuls les rangs A et B comptent** dans la couverture et la mise à jour
   (au minimum en pneumologie et en neurologie). Le rang C n'est pas à apprendre.
2. **On ne supprime jamais de carte** au motif qu'elle porte sur du rang C :
   une même note peut couvrir une connaissance de rang A ou B ailleurs.
3. Un objectif dont le rang est inconnu est marqué **« à clarifier »**, pas
   compté d'office.
4. Une donnée non vérifiée contre une édition identifiée n'est jamais présentée
   comme vérifiée. Aucun numéro d'item n'est inventé.

## Sources

- **Anki EDN (C2SU)** : https://c2su.github.io/Anki_EDN/
  Reprise collaborative du travail de Léo Picat, hébergée par des étudiants de
  Sorbonne. Sa documentation cite un autre Drive, distinct du nôtre.
- **Drive fourni** : https://drive.google.com/drive/folders/1w3NoLnODfW1L69wGdNmbTrWEJHCyuOIR
- **« Lisez-moi Anki.pdf »** : à lire **en premier**, avant toute fusion.

La fusion des différentes versions est reportée : il faut d'abord identifier
quelle version contient quoi.

## Système de contrôle

Le système local est disponible dans `web/` ; [le mode d’emploi](docs/mode-emploi.md) détaille l’import des paquets et la relecture objectif par objectif.

```sh
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python lancer.py
```

Sous Windows : utiliser `.venv\Scripts\python.exe` pour les deux dernières commandes. Le serveur écoute uniquement sur l’interface locale. Aucun paquet n’est fusionné ni modifié ; les exports Anki restent hors Git.

- [Registre des sources et chapitres](data/references.json) et [tableau initial CSV](data/suivi-initial.csv).
- [Règle A/B et conservation des connaissances C](docs/regle-rangs.md).
- [Identification des paquets et Drives](docs/identite-paquets.md).
- [Validation du logiciel et limites](docs/validation.md).

Les 51 entrées sont des chapitres issus des textes fournis, pas 51 items nationaux validés ni une preuve de couverture du programme. Un rang inconnu reste à clarifier. Les anciennes validations pneumo/neuro sont à reprendre sous la règle A/B, sans suppression de cartes.

Tests : `python -m unittest discover -s tests -v`. Régressions navigateur facultatives, avec Playwright et Chromium : `python tests/browser_smoke.py` et `python tests/ranks_browser.py`. Page autonome et archive : `python construire.py`.

## Collaboration (Claude et Codex)

- `main` reste stable : on n'y pousse pas directement.
- Chaque agent travaille sur sa branche : `codex/<sujet>`, `claude/<sujet>`.
- On pousse souvent et on fusionne par pull request, relue par l'autre agent ou
  par un humain.
- Les exports Anki (`.apkg`, `.colpkg`) ne sont pas versionnés (voir `.gitignore`).
