# Constats préliminaires sur les sources

**État du contrôle : documentation inspectée ; paquet Anki réel non importé.** Aucune carte n'a donc encore été déclarée présente, absente ou conforme à une édition récente. Aucun résultat ne démontre la couverture de toutes les spécialités demandées.

## Site Anki EDN : ce que l'on peut établir

La copie locale du dépôt public [`c2su/Anki_EDN`](https://github.com/c2su/Anki_EDN/tree/fceb5bf186c9641bb978cc891c8c8c8a797fe289), au commit exact **`fceb5bf186c9641bb978cc891c8c8c8a797fe289`**, a été inspectée. Ce dépôt contient le site et sa documentation : aucun fichier de paquet `.apkg`/`.colpkg` ou de collection `.anki2`/`.anki21`/`.anki21b` n'y a été trouvé. L'état de ce commit ne donne pas la version du paquet actuellement installé chez vous.

- [Installation](https://github.com/c2su/Anki_EDN/blob/fceb5bf186c9641bb978cc891c8c8c8a797fe289/src/installation.md) : le téléchargement et les mises à jour du paquet passent par **AnkiCollab**, avec compte, greffon et abonnement. Le site seul ne fournit donc pas l'inventaire de vos notes.
- [Mises à jour des items](https://github.com/c2su/Anki_EDN/blob/fceb5bf186c9641bb978cc891c8c8c8a797fe289/src/mises_a_jour.md) : un [tableau Google Sheets de suivi](https://docs.google.com/spreadsheets/d/1EpIQmvkDmqrqDy4YTaygqLuE0qrh2Q_t8FdQx6AdEhU/edit) existe. **Son lien a été constaté ; son contenu n'est pas ici audité.** Une déclaration de mise à jour doit être confrontée à l'édition du collège et aux notes effectivement importées.
- [Modification du paquet](https://github.com/c2su/Anki_EDN/blob/fceb5bf186c9641bb978cc891c8c8c8a797fe289/src/modifier.md) : les étiquettes attendues suivent notamment `EDN::item-numéro-intitulé`. Les tags `Ankicollab_protect::all` ou de champ peuvent empêcher certaines mises à jour locales ; la synchronisation seule ne prouve donc pas la conformité de votre copie.
- [FAQ](https://github.com/c2su/Anki_EDN/blob/fceb5bf186c9641bb978cc891c8c8c8a797fe289/src/FAQ.md) : le paquet est présenté comme une préparation aux **EDN**, et explicitement **pas aux ECOS**. Les nouveaux encadrés ECOS du CEP constituent un périmètre supplémentaire à décider, pas une couverture à supposer.
- [Introduction](https://github.com/c2su/Anki_EDN/blob/fceb5bf186c9641bb978cc891c8c8c8a797fe289/src/Introduction.md) : la mention « presque exhaustif » reste une présentation du projet, pas une preuve d'exhaustivité.

## Textes collés par l'utilisateur : inventaire observable

| Texte fourni | Ce qui est réellement listé | Limite de preuve |
| --- | --- | --- |
| Collège des enseignants de pneumologie (CEP) | **22 entrées de chapitres**, dont `359` et `359 bis` distincts ; 21 bases numériques. Le lien EFR supplémentaire n'est pas un 23e item numéroté. | Le texte annonce la **9e édition**, un article du **10 septembre 2026** et une mise à jour du **15 septembre 2026**. Ces mentions ne prouvent ni que chaque PDF possède cette version, ni que les Anki l'intègrent. |
| Collège des enseignants de neurologie (CEN) | **29 titres de chapitres**, sans numéro d'item : 26 suivis de « En savoir plus sur… » et 3 de « En savoir plus » seulement. | Le bandeau parle encore de l'**ECN 2022** et des 5e/6e éditions. L'édition actuellement pertinente reste à établir ; aucun numéro n'est déduit du titre seul. |

Les trois entrées CEN facilement omises par un extracteur sont **Altération aiguë de la vision**, **Hémorragie méningée non traumatique**, **Trouble aigu de la parole. Dysphonie**. Certains chapitres regroupent plusieurs thèmes ; un chapitre ne correspond pas nécessairement à un seul item national. Les textes collés ne conservent pas les URL des pages et des téléchargements : leur provenance web précise devra être ajoutée.

Ces deux inventaires ne définissent pas le programme complet des EDN. Les éditions récentes de néphrologie, orthopédie, cancérologie et santé publique sont maintenant [documentées](../sources/README.md) ; leurs objectifs A/B restent à inventorier. Le dossier Drive transmis ne constitue pas, par sa seule URL, un paquet analysé ni une preuve de contenu.

## Condition d'une validation utilisable

Pour chaque objectif retenu : conserver **source et édition, chapitre/page/section, notes Anki identifiables, constat de comparaison, relecteur et date**. Une étiquette ou un rapprochement automatique sert à repérer les notes ; il ne valide pas leur actualité médicale. La date de modification Anki ne suffit pas. Une validation doit être réexaminée si les notes ou la source changent. Les zones non examinées restent visibles comme telles.
