# Validation et limites de livraison

Vérifications du 6 novembre 2026 dans l’environnement de développement :

- **29 tests Python réussis**, aucun test ignoré : 18 tests d’import, 5 tests du registre source, 6 tests HTTP locaux.
- Les importations testées utilisent de vraies bases SQLite et archives Anki **synthétiques**, y compris le format récent Zstandard et les fichiers de compatibilité factices. Elles ne représentent pas vos cartes médicales.
- Le serveur a reçu des requêtes fonctionnelles d’import : contenu et métadonnées attendus retrouvés ; un paquet corrompu est rejeté, sans succès vide.
- Le registre fourni correspond aux textes conservés : 22 entrées CEP, 29 chapitres CEN, numéros neurologiques inconnus, `359` et `359 bis` distincts ; quatre autres spécialités signalées sans source.
- Analyse syntaxique Python et JavaScript réussie.
- Page HTML autonome générée : 51 entrées, aucun inventaire initial, aucune erreur JavaScript lors de son exécution sans ressources externes.
- Parcours dans Chromium : inventaire importé, suggestion sans validation automatique, objectif relu avec preuve, validation sur une version puis invalidation après changement d’inventaire, sauvegarde et export des objectifs. Contrôles avec données synthétiques ; aucun diagnostic médical tiré de ces tests.

Pour reproduire les tests du logiciel : `python -m unittest discover -s tests -v`, depuis la racine du dossier. Les tests HTTP demandent l’autorisation de créer un serveur sur l’interface locale. Le lanceur a la même exigence, qui existe normalement sur un ordinateur personnel.

## Ce qui n’a pas été vérifié

Aucun paquet réel du dossier Drive n’a été lu ; aucun chapitre complet officiel récent n’a été comparé à des cartes. Il n’y a donc ni taux de couverture Anki établi, ni item médical déclaré à jour. Le contrôle final doit porter sur la version réellement exportée depuis Anki et sur le référentiel applicable à votre session.

Le mode fichier `web/index.html` ne dépend d’aucun réseau ni serveur et ne fait pas de requêtes pour ses imports JSON. La navigation `file://` est bloquée par le navigateur administré de l’environnement de développement ; le parcours visuel a donc été testé via le serveur local. L’import APKG passe par le lanceur local.

## Accès réseau de l’environnement

Le dépôt documentaire public C2SU était accessible via GitHub. Les accès directs à `c2su.github.io` et `drive.google.com` étaient refusés par la politique réseau. Le lien de suivi des mises à jour utilise `docs.google.com`.

Les trois domaines `c2su.github.io`, `drive.google.com`, `docs.google.com` ont été **enregistrés dans le brouillon** de configuration réseau, en conservant le préréglage existant. Cette sauvegarde n’a ni ouvert l’accès dans la machine ni publié l’environnement. Pour utiliser ces accès depuis cette machine, revoir et enregistrer les modifications dans les paramètres de l’environnement, puis publier l’environnement. Les éventuels droits de partage Drive restent à vérifier séparément. Aucun identifiant ni secret n’a été demandé.

L’outil local livré fonctionne sans cet accès : il suffit d’importer les fichiers exportés depuis Anki et de consulter soi-même les sources officielles.

La régression navigateur est conservée dans `tests/browser_smoke.py` : import APKG par l’API, contrôle objectif par objectif, invalidation des versions, historique, retrait des anciennes associations, sauvegarde/restauration JSON, CSV et avertissement persistant de quota. Elle nécessite Playwright et Chromium uniquement pour le développement.

## Contrôle du périmètre A/B en pneumologie et neurologie

La régression `python tests/ranks_browser.py` vérifie, avec des connaissances **synthétiques** : seuls A/B justifiés comptent ; C absent ou divergent n’empêche pas la validation A/B ; les objectifs C et les notes partagées restent conservés ; le même contenu peut être C dans un collège et B dans l’autre ; un rang inconnu ou C sans preuve bloque la validation complète ; un ensemble uniquement C ne valide pas un périmètre A/B ; une ancienne association C indisponible ne bloque pas la revalidation A/B. Les anciennes validations sont à reprendre et les autres spécialités conservent leurs règles. Les exports conservent le détail des exclusions et des rangs inconnus.

Ces contrôles valident la règle logicielle. Aucun rang réel de connaissance ni aucune conformité médicale n’a été déduit des seuls titres des chapitres.
