# Contrôle des collèges ↔ Anki EDN

Un outil local pour vérifier **vous-mêmes** la présence des sujets et la conformité des cartes à une version identifiée du collège. Le rapprochement automatique repère des candidats ; la validation du contenu reste explicite, documentée et humaine.

**État initial :** 22 entrées de pneumologie + 29 chapitres de neurologie recensés depuis vos textes. Aucun de vos paquets Anki n’a encore été importé. Aucun item n’est déclaré à jour. Les inventaires d’objectifs de néphrologie, orthopédie, cancérologie et santé publique restent à ajouter. Ces 51 entrées ne constituent pas la liste nationale de tous les items EDN. Les quatre autres référentiels ont maintenant une [fiche bibliographique](../sources/README.md) ; leurs objectifs ne sont pas encore intégrés.

## Périmètre : rangs A et B uniquement dans chaque collège

Pour **chaque collège** du projet, la couverture et la mise à jour portent uniquement sur les connaissances de **rang A et B**. Le **rang C n’est pas compté** dans les objectifs à couvrir ni dans les objectifs conformes, et ne nécessite pas de mise à jour dans ce périmètre.

La classification s’applique à **chaque connaissance dans le collège concerné**, jamais globalement à une carte. Une même note peut contenir un objectif C en pneumologie et un objectif B en neurologie, ou mélanger des informations de plusieurs rangs. **Ne supprimer, ne suspendre et ne modifier aucune carte à cause d’un classement C.** L’outil conserve les notes et les objectifs C pour la traçabilité.

Si une ligne regroupe des connaissances de rangs différents, la séparer en plusieurs objectifs du registre, sans découper ni supprimer la carte Anki. Dans chaque objectif, sélectionner A, B, C ou « à déterminer » et renseigner le repère de la source qui justifie ce rang. Les tags Anki ou un rang écrit en texte libre ne remplacent pas cette confirmation. Un rang inconnu reste à clarifier ; il ne vaut ni A/B ni exclusion C. Un classement C sans justification ne permet pas de valider le chapitre.

L’interface et les exports distinguent les objectifs A/B attendus et conformes, le C exclu et les rangs à clarifier. Un chapitre contenant seulement des objectifs C ne devient pas « vérifié A/B » : il faut établir la liste réelle de ses objectifs A/B. Les validations enregistrées sous une ancienne politique sont à reprendre, sans perdre les relectures ou les cartes. Les règles du dépôt main imposent désormais cette politique A/B par défaut à tout collège ajouté ; la classification reste indépendante selon la source.

## Démarrer

1. Décompressez le dossier sur votre ordinateur. Python **3.10 ou plus récent** est nécessaire pour l’import des paquets.
2. Dans ce dossier, ouvrez un terminal et lancez :

   ```sh
   python -m venv .venv
   # macOS / Linux :
   .venv/bin/python -m pip install -r requirements.txt
   .venv/bin/python lancer.py
   # Windows : utilisez plutôt les deux commandes suivantes
   # .venv\Scripts\python.exe -m pip install -r requirements.txt
   # .venv\Scripts\python.exe lancer.py
   ```

   Si la commande `python` n’existe pas sur macOS/Linux, utilisez `python3` à la première ligne. Le navigateur s’ouvre. Gardez le terminal ouvert pendant l’utilisation, puis arrêtez avec Ctrl+C.
3. Dans l’interface, importez un paquet `.apkg` / `.colpkg`, une collection `.anki2`, ou un export de notes `.txt` / `.tsv`. L’import local est en lecture seule ; il ne modifie jamais Anki. Les médias et les greffons ne sont pas exécutés.

**Sans installation :** ouvrez la page autonome `Controle-EDN.html` livrée dans l’archive (ou `web/index.html` dans le dossier source) dans votre navigateur. Toutes les fonctions de contrôle et de sauvegarde fonctionnent à partir d’un inventaire JSON déjà produit. L’import direct d’un paquet nécessite le lanceur Python. L’interface n’utilise aucun service distant.

## Préparer les vrais paquets

Dans Anki sur ordinateur : exporter le paquet concerné au format `.apkg` (ou la collection complète en `.colpkg`). Ne pas exporter uniquement les cartes sélectionnées si vous voulez vérifier l’ensemble. Inclure les cartes suspendues : une carte suspendue peut bien être présente. Vous pouvez désactiver l’inclusion des médias pour réduire la taille du fichier ; ils seront contrôlés dans Anki. L’import dans l’interface accepte jusqu’à 256 Mio ; pour un fichier plus gros, utiliser la commande ci-dessous (limite 1 Gio) ou exporter sans médias. Un export de **notes** TXT avec les tags est également exploitable, mais il ne donne pas toujours les identifiants de notes, les paquets et le nombre de cartes.

Pour agréger plusieurs fichiers dans un seul inventaire :

```sh
python edn_audit.py import "Pneumo.apkg" "Neuro.apkg" --out inventaire.json
```

Puis importer `inventaire.json` dans l’interface. Un import technique complet signifie seulement que les fichiers fournis ont été lus, **pas** que tous vos paquets ou tous les EDN ont été fournis. L’interface remplace l’inventaire courant lors d’un nouvel import ; sauvegardez auparavant et utilisez la commande ci-dessus pour plusieurs fichiers. Les doublons de fichiers ou d’identifiants entre exports ne constituent pas des objectifs supplémentaires.

## Contrôler un chapitre

1. **Identifier la source.** Ouvrir le site du collège, contrôler l’édition qui s’applique à votre session EDN, les éventuels errata et le périmètre rangs A/B/ECOS. Enregistrer l’URL officielle et l’édition. Le texte fourni n’établit pas à lui seul la dernière édition publiée.
2. **Confirmer la correspondance.** Examiner les notes candidates et leurs tags ; contrôler le numéro dans la nomenclature de référence. Pour la neurologie, aucun numéro n’est deviné : vous confirmez la correspondance après lecture de la source. Un chapitre peut regrouper plusieurs items. `359` et `359 bis` restent distincts.
3. **Lister les objectifs attendus.** Pour chaque collège, recenser tous les objectifs A/B du chapitre et justifier séparément les exclusions C ; un rang inconnu est à clarifier, avec page/section/identifiant de connaissance et rang quand il est disponible. Une simple liste de titres ne constitue pas ce travail.
4. **Vérifier chacun.** Pour chaque objectif : indiquer le repère source, les identifiants des notes et le verdict. Vérifier en particulier les chiffres, seuils, algorithmes, diagnostics, traitements, contre-indications et changements d’édition. Ouvrir les cartes dans Anki pour les images, sons et schémas ; l’aperçu de l’outil est textuel.
5. **Consigner la relecture.** Renseigner relecteur, date, justification et confirmation du périmètre exhaustif. Une couverture partielle ou un échantillon ne doit pas être présenté comme un chapitre entièrement vérifié. Une contradiction ou un objectif absent reste visible comme écart.
6. **Partager la preuve.** Exporter le CSV pour un tableur et la sauvegarde JSON pour reprendre le travail ou le transmettre à un autre relecteur. Le CSV est une restitution ; la sauvegarde JSON conserve l’état complet.

Une présence de tag est une **piste**. « Non retrouvé » signifie non retrouvé dans les fichiers importés, et non absent de tous les Anki. « Vérifié sur cette version » décrit une relecture datée sur un périmètre déclaré ; ce n’est pas une garantie médicale ni une veille en temps réel.

## Mettre à jour et étendre aux autres collèges

- Après une mise à jour Anki : réexporter et réimporter les paquets. Les empreintes de fichiers empêchent de réutiliser silencieusement une validation sur un autre inventaire. Cette invalidation est conservatrice : un changement de fichier peut faire demander une relecture même si le contenu pédagogique n’a pas changé.
- Après une nouvelle édition ou un erratum : mettre à jour le registre des sources et sa liste d’objectifs. Une version ne s’actualise pas automatiquement depuis le Web. L’édition et l’URL seules ne détectent pas toutes les modifications d’une page : conserver aussi les fichiers sources et recalculer leur empreinte.
- `data/references.json` est le registre lisible et modifiable : sources, empreintes SHA-256, spécialités, chapitres et numéros. Importer une nouvelle version dans l’interface pour ajouter les collèges manquants. Garder un identifiant stable pour la même entrée ; changer le hash source quand son contenu change. `web/seed.js` contient seulement la copie initiale pour le premier démarrage.
- Empreinte d’un fichier, sans l’envoyer ailleurs :

  ```sh
  python -c "import hashlib,pathlib; print(hashlib.sha256(pathlib.Path('referentiel.pdf').read_bytes()).hexdigest())"
  ```

- Ne pas transformer automatiquement un titre en numéro national, ni assimiler un ancien numéro ECN à un numéro R2C. Vérifier les correspondances dans une source applicable à votre session et enregistrer le repère.

Exemple de source à ajouter au registre (valeurs à remplacer par les données constatées) :

```json
{
  "id": "college-specialite-edition",
  "specialty": "Néphrologie",
  "title": "Titre de la source officielle",
  "edition": "Édition vérifiée",
  "url": "https://exemple.fr/referentiel",
  "sha256": "EMPREINTE_SHA256_DU_FICHIER_SOURCE",
  "edition_status": "unknown",
  "limitation": "Contrôler l’édition applicable et les errata"
}
```

Et une entrée dans `items`, liée à cette source :

```json
{
  "id": "specialite:identifiant-stable",
  "source_id": "college-specialite-edition",
  "number": null,
  "title": "Intitulé du chapitre",
  "number_status": "unknown"
}
```

Utiliser `null` tant que le numéro n’est pas vérifié. S’il est connu, le conserver comme **texte**, par exemple `"359 bis"`. Préserver aussi les entrées déjà recensées lors d’un remplacement du registre et compléter `scope` pour les spécialités ajoutées.

## Sources et limites actuelles

Voir [les constats sourcés](constats-sources.md) et les [textes conservés](../data/sources). La documentation publique Anki EDN signale un tableau de mises à jour et le téléchargement via AnkiCollab ; elle ne contient pas les cartes. Certains tags de protection AnkiCollab peuvent empêcher des mises à jour locales. Une synchronisation réussie ne démontre donc pas l’actualité du contenu.

Les accès directs au site C2SU et au dossier Drive étaient refusés par la politique réseau de la machine lors de la préparation. Le Lisez-moi est désormais lu et résumé dans `sources/lisez-moi.md` ; les paquets Anki réels et les livres complets récents n’ont pas été audités. Les nombres initiaux sont des nombres de chapitres, et non des nombres de connaissances A/B. Aucun rang n’est déduit de ces seules listes. Ils proviennent exclusivement des textes fournis ; le dépôt documentaire public C2SU a été consulté au commit `fceb5bf186c9641bb978cc891c8c8c8a797fe289`.

Le paquet déclare ne pas préparer aux ECOS, tandis que le texte CEP annonce des ajouts ECOS : le périmètre doit donc être documenté, sans prétendre couvrir automatiquement ces nouveautés.

## Sauvegardes et confidentialité

Les cartes restent sur votre ordinateur. Le serveur écoute uniquement sur l’adresse de boucle locale ; aucun compte distant n’est requis. L’état est enregistré dans le stockage du navigateur quand celui-ci le permet ; exportez régulièrement la sauvegarde JSON, surtout avant de changer de navigateur, de port ou d’ordinateur. Sans sauvegarde, vider les données du navigateur peut perdre les relectures.

Le JSON et le CSV peuvent contenir des extraits de cartes : partagez-les seulement dans le cadre autorisé par leurs auteurs. Aucun identifiant de compte Anki ni mot de passe n’est nécessaire. L’outil ne corrige pas automatiquement vos cartes.

## Vérifier le logiciel

```sh
python -m unittest discover -s tests -v
```

Les tests utilisent des paquets **synthétiques**, distincts des données initiales. Leur succès valide l’import et les règles du logiciel, pas l’actualité médicale des cartes réelles.

Pour reconstruire la page autonome et l’archive depuis les sources : `python construire.py`. La régression navigateur facultative se lance avec `python tests/browser_smoke.py` dans un environnement de développement équipé de Playwright et de Chromium ; ces outils ne sont pas nécessaires pour utiliser le contrôleur.

## Recherche des autres collèges et identification du Drive

Le panneau « Sources, éditions et périmètre » contient les résultats des quatre recherches et le lien du Lisez-moi lu. Les éditions sont identifiées bibliographiquement ; les objectifs et cartes restent **à contrôler**, sans validation médicale présumée. Les liens s’ouvrent dans votre navigateur. Consulter aussi `docs/identite-paquets.md`. Pour appliquer cette mise à jour dans une interface déjà utilisée, sauvegarder vos données puis charger `data/references.json` avec « Charger un référentiel JSON ». Les correspondances et relectures existantes sont conservées ; ne pas réinitialiser votre navigateur.

### Après ouverture du réseau

Le blocage décrit historiquement ci-dessus est résolu. Le Lisez-moi du Drive est [lu et résumé](../sources/lisez-moi.md) et les quatre référentiels ont une fiche dans `sources/`. Cela ne certifie aucune carte médicale. Le panneau des recherches reflète ces résultats, en distinguant l’édition récente du contenu gratuit plus ancien.
