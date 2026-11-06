# Tâches — mise à jour du Deck EDN - MEA

Méthode obligatoire : `audit/PROTOCOLE.md`. Avancement à jour à tout moment :
`python outils/valider_audit.py --avancement`.

## Phase 1 — Pneumologie : audit contre le CEP 9e (2026)

Faits : **204 Toux · 205 Hémoptysie · 360 Pneumothorax** (Claude, 2026-11-06).

À faire, répartis en lots indépendants (fichiers distincts : plusieurs lots peuvent tourner en
parallèle sans conflit). Un lot = une tâche Codex = une branche `codex/audit-pneumo-lot-X`.

| Lot | Items | Notes MEA (hors pédiatrie) | Objectifs A/B | Remarque |
|---|---|---|---|---|
| A | 75 Tabac · 110 Sommeil · 154 Infections respiratoires | 125 · 175 · 172 | 32 · 16 · 17 | 110 rangé en NEUROLOGIE, 154 en INFECTIOLOGIE : statut `divergent (autre collège)` possible |
| B | 159 Tuberculose · 186 Hypersensibilité · 188 Asthme | 188 · 236 · 174 | 17 · 18 · 25 | 159 en INFECTIOLOGIE ; 186 réparti (médecine interne, travail) |
| C | 203 Dyspnée · 206 Épanchement pleural · 207 Opacités | 118 · 100 · 221 | 16 · 7 · 9 | 207 vise aussi l'enfant : inclure la pédiatrie (`--exclure`) |
| D | 208 IRC · 209 BPCO · 210 PID | 263 · 229 · 0 | 12 · 14 · 13 | 210 : aucune carte (déclaré absent par l'auteur) → 13 × `non retrouvé` + cartes `nouvelle` |
| E | 211 Sarcoïdose · 226 MTEV · 230 Douleur thoracique | 148 · 199 · 91 | 14 · 18 · 14 | 226 et 230 rangés surtout en CARDIOLOGIE ; fichier CEP « Item-226-330 » |
| F | 309 Cancer · 338 Anaphylaxie · 359 Détresse respiratoire · 359 bis Corps étranger | 121 · 160 · 183 · (sous 359) | 13 · 12 · 16 · 7 | 359 bis : notes rangées sous 359, inclure la pédiatrie |

Case à cocher quand la PR du lot est fusionnée **après relecture** :

- [ ] Lot A  - [ ] Lot B  - [ ] Lot C  - [ ] Lot D  - [ ] Lot E  - [ ] Lot F

## Phase 2 — Relecture (obligatoire avant toute modification du deck)

1. Relecture de chaque PR par un second agent (Claude) : nid, statuts, fidélité à la 9e.
2. Relecture humaine : au minimum tous les objectifs `à mettre à jour` et `divergent`, puis
   un échantillon de `conforme`. Remplir `relu_par` / `relu_le`.

## Phase 3 — Neurologie (bloquée, ne pas commencer)

Source à établir : édition du Collège des Enseignants de Neurologie applicable, liste des
objectifs avec leur rang A/B. Décision humaine requise avant tout audit.

## Phase 4 — Produire le deck corrigé (après la phase 2)

Appliquer les corrections relues aux notes existantes en conservant leur identifiant (GUID),
pour garder l'historique de révision ; ajouter les cartes `nouvelle` dans un sous-paquet
identifié. Non délégué : à faire avec Claude et validation humaine.

## Phase 5 — Deck Léo Picat / C2SU (Sorbonne)

À examiner séparément ; ne pas fusionner avec le deck MEA.
