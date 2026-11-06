# Identifier les paquets et les Drives avant toute fusion

**Contrôle local du 6 novembre 2026.** Ce document s’appuie sur la copie du site public `c2su/Anki_EDN`, branche `site`, au commit **`fceb5bf186c9641bb978cc891c8c8c8a797fe289`**. Il ne repose sur aucune lecture du dossier Drive de l’utilisateur ni d’un PDF « Lisez-moi Anki ».

## Ce qui relie Léo Picat, Sorbonne et Anki EDN

L’[introduction du site](https://github.com/c2su/Anki_EDN/blob/fceb5bf186c9641bb978cc891c8c8c8a797fe289/src/Introduction.md) indique explicitement qu’**Anki EDN se base sur le travail et la méthodologie de Léo Picat**, et vise à rendre son paquet collaboratif et communautaire.

Les [remerciements](https://github.com/c2su/Anki_EDN/blob/fceb5bf186c9641bb978cc891c8c8c8a797fe289/src/remerciement.md) précisent que le projet est hébergé par la **Corporation des Carabins de Sorbonne Université**, via le pôle informatique. Ce sont des indices directs qui correspondent au souvenir d’un paquet Picat repris par des étudiants de Sorbonne. Ils ne prouvent pas que le Drive donné contient cette version.

L’[installation](https://github.com/c2su/Anki_EDN/blob/fceb5bf186c9641bb978cc891c8c8c8a797fe289/src/installation.md) décrit un téléchargement via **AnkiCollab**, abonnement public `mango-may-georgia-eleven-moon-orange`, ainsi que la recherche de mises à jour au démarrage. La présence de ce code dans un document permettrait d’établir une correspondance documentaire ; elle ne garantirait pas l’identité exacte des cartes ni leur actualité.

## Registre des liens distincts

| Ensemble ou document | Lien constaté | Preuve et statut | Ce qui reste inconnu |
| --- | --- | --- | --- |
| **Anki EDN / C2SU** | [Site](https://c2su.github.io/Anki_EDN/) ; [sources documentaires](https://github.com/c2su/Anki_EDN/tree/fceb5bf186c9641bb978cc891c8c8c8a797fe289/src) | **Documentation lue localement**, commit ci-dessus. Filière de distribution AnkiCollab explicitement décrite. | Version actuelle du paquet et version installée chez l’utilisateur. Le dépôt documentaire ne contient pas de `.apkg` ou de collection Anki à comparer. |
| **Travail initial de Léo Picat** | [Documentation citée par C2SU](https://picat.fr/2024/06/02/paquet-anki-edn.html) | **Lien constaté**, document distant non lu dans cette recherche locale. L’origine Picat est affirmée dans l’introduction C2SU. | Fichiers et versions actuellement proposés par cette page ; égalité avec les cartes du Drive de l’utilisateur. La date dans le chemin URL ne prouve pas une version de paquet. |
| **Drive fourni par l’utilisateur** | [Dossier `1w3NoLnODfW1L69wGdNmbTrWEJHCyuOIR`](https://drive.google.com/drive/folders/1w3NoLnODfW1L69wGdNmbTrWEJHCyuOIR) | **URL fournie ; contenu non lu.** Aucun PDF de ce dossier n’a été inspecté. | Nom et auteur du paquet, version, éventuelle fusion, provenance et contenu du « Lisez-moi Anki.pdf ». |
| **Autre Drive cité dans l’introduction C2SU** | [Dossier `1M9hg4EMRoFRQ4wh_E2xIOu_bKmg7ze59`](https://drive.google.com/drive/u/0/folders/1M9hg4EMRoFRQ4wh_E2xIOu_bKmg7ze59) | **Lien constaté dans `Introduction.md`**, sous « Je n’ai jamais utilisé Anki » ; contenu non lu. L’identifiant est différent du dossier utilisateur. | Contenu, propriétaire, paquet éventuellement distribué. Deux dossiers distincts peuvent distribuer le même paquet ou des variantes : cela reste à vérifier. |
| **Document d’initiation cité par C2SU** | [Fichier `1UWSg3gj3PyIJq0oXetesZVlbJuRGxLrA`](https://drive.google.com/file/d/1UWSg3gj3PyIJq0oXetesZVlbJuRGxLrA/view) | **Lien constaté dans `Introduction.md`**, présenté seulement comme « ce document » ; contenu non lu. | Son titre, son format exact, sa version et son identité éventuelle avec le « Lisez-moi Anki.pdf » mentionné par l’utilisateur. Ne pas les assimiler sans lecture. |
| **Tableau C2SU des mises à jour** | [Google Sheets](https://docs.google.com/spreadsheets/d/1EpIQmvkDmqrqDy4YTaygqLuE0qrh2Q_t8FdQx6AdEhU/edit) | **Lien constaté** dans [`mises_a_jour.md`](https://github.com/c2su/Anki_EDN/blob/fceb5bf186c9641bb978cc891c8c8c8a797fe289/src/mises_a_jour.md) ; tableau distant non lu. | Dernière date déclarée par item, référentiels concernés et adéquation aux notes réellement exportées. |

## Piste Facebook et communauté

L’introduction C2SU donne un lien vers le groupe Facebook **[La communauté des externes utilisant Anki](https://www.facebook.com/groups/anki.ecni)** ainsi que [son Discord](https://discord.gg/2A7zHAEBYt). Les liens sont constatés dans les sources au commit ci-dessus. **Aucune publication Facebook ou Discord n’a été lue**, et aucune annonce de nouvelle version n’en est déduite.

Le lien publié du tableau intégré est aussi conservé dans `mises_a_jour.md` :

`https://docs.google.com/spreadsheets/d/e/2PACX-1vQWeHJNksMrjEWhF6egJk2SjVVYPER7SZumpfqkrPFS6XGlNvX10TU5MvyaQIiWbH1_BlKLm10f0n66/pubhtml?gid=1009852412&single=true&widget=true&headers=false`

## Informations à relever dans le « Lisez-moi »

À la lecture effective du fichier du Drive utilisateur, relever : titre exact ; auteur et collectif ; date/version explicitement annoncée ; paquet(s) à télécharger ; source initiale ; éventuels ajouts/fusions ; mode de mise à jour ; lien AnkiCollab et abonnement le cas échéant ; périmètre des spécialités ; référentiels/éditions déclarés ; consignes concernant les doublons et les identifiants de notes. Conserver le fichier et son empreinte SHA-256 pour rattacher ces mentions à une version précise du document.

Une identification documentaire doit ensuite être confrontée aux **GUID, types de notes, tags, contenu et empreintes** des paquets. Des noms ressemblants ne suffisent pas pour fusionner des fichiers. La consigne actuelle est de garder les ensembles séparés.

## Ce qu’une mise à jour réussie ne prouve pas

La [documentation de modification C2SU](https://github.com/c2su/Anki_EDN/blob/fceb5bf186c9641bb978cc891c8c8c8a797fe289/src/modifier.md) précise que `Ankicollab_protect::all` ou un tag de champ tel que `Ankicollab_protect::verso` peut protéger du contenu contre les mises à jour. Elle distingue les tags `MAJ` et `NEW`. Ainsi, une connexion ou une synchronisation réussie ne prouve ni la mise à jour de chaque champ de la copie locale ni sa conformité au dernier collège.
