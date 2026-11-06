# Lecture du « LISEZ-MOI anki.pdf » du Drive fourni

**Document lu le 6 novembre 2026 : 17 pages**, texte et exemples illustrés des pages 3 à 7. Le PDF décrit **Deck EDN - MEA**, signé **Mohamed El Amri** (p. 9). Il ne doit pas être assimilé au paquet Picat/C2SU sans comparaison des fichiers et des notes.

## Source et version du document

- [Dossier fourni](https://drive.google.com/drive/folders/1w3NoLnODfW1L69wGdNmbTrWEJHCyuOIR).
- [Fichier exact « LISEZ-MOI anki.pdf »](https://drive.google.com/file/d/1D54QcKxh_4ZkDEvvX16K4K3zlsEsbRns/view).
- [Téléchargement public du même fichier](https://drive.usercontent.google.com/download?id=1D54QcKxh_4ZkDEvvX16K4K3zlsEsbRns&export=download).
- Empreinte SHA-256 : `26a83864e5e368d2630a82dc67e0beee9fecfb8ea0b03e0e6e3e6776f47a64af` ; taille : **2 945 858 octets**.
- Les métadonnées techniques de création/modification indiquent **28 octobre 2026, 13 h 20 min 04 s UTC**. Ce n’est pas une date de conformité médicale des cartes. Aucune édition des collèges, détaillée item par item, n’est identifiée dans ce PDF.
- Le dossier consulté contient aussi un export PDF nommé **Deck EDN - MEA 2026-10-28.pdf** et un paquet **Deck EDN - MEA.apkg**. Leur présence et leurs noms ont été constatés ; leur contenu n’a pas été audité dans cette lecture. Le nom daté du PDF ne date pas à lui seul le contenu médical du paquet APKG.

Les métadonnées et la méthode de lecture sont conservées dans [preuves/lisez-moi.json](preuves/lisez-moi.json). Le PDF original n’est pas ajouté à Git.

## Ce que propose l’auteur

**Méthode pédagogique (p. 1–8).** Des questions ciblées portent sur des faits précis, tandis que le verso conserve un cours ou tableau plus développé pour préserver le contexte clinique. Le document recommande des formulations compréhensibles par un autre externe et utilise des comparaisons entre notions. Les exemples en images illustrent ce format ; ils ne constituent pas une vérification de leurs recommandations médicales.

**Périmètre annoncé (p. 8).** L’auteur cite les collèges et LiSA comme supports de travail pour chaque item. Il annonce environ **43 000 cartes**, ainsi qu’un paquet ACE issu de ses erreurs et un paquet LCA. Ce sont des déclarations du document, pas des décomptes effectués dans le fichier Anki.

**Allègement sans suppression (p. 8).** Plusieurs notes partagent un même verso, notamment une ligne ciblée par question sur un tableau commun. Le tag `TOUR-doublon` sert à masquer ces répétitions à la révision en conservant une note hors tag dans chaque groupe. L’auteur annonce environ **42 800 cartes** pour le deck complet et **26 800** pour la sélection allégée.

Recherches Anki documentées :

```text
deck:"Deck EDN - MEA"
deck:"Deck EDN - MEA" -tag:TOUR-doublon
```

Ce filtre sert à l’organisation des révisions : **il ne faut pas l’utiliser pour retirer des notes de l’inventaire d’audit**, ni le confondre avec un classement A/B/C. Une note portant ce tag peut conserver une information utile.

## Lacunes explicitement déclarées dans le PDF

Les pages **8–9** déclarent **14 numéros absents** :

`60`, `62`, `70`, `118`, `119`, `130`, `177`, `179`, `202`, `210`, `212`, `231`, `327`, `333`.

Il s’agit de la numérotation **déclarée dans le document**, pas d’une correspondance nationale recalculée. Ces absences restent à contrôler contre le paquet réel et l’édition applicable. En particulier, le document cite l’**item 210, pneumopathies interstitielles diffuses**, qui figure aussi dans le texte CEP fourni : c’est une **priorité de recherche de couverture**, pas encore une absence constatée par import Anki.

Le PDF ne donne pas de matrice d’objectifs A/B ni de justification permettant d’exclure ces lacunes comme du rang C. Le projet conserve donc sa règle : **vérifier les connaissances A/B dans la source de chaque collège, sans supprimer de carte C**.

## Installation et greffons : ce qui est décrit, sans exécution

- **P. 9 :** Anki sur ordinateur **25.07 ou ultérieur**, installation des greffons puis redémarrage avant l’import APKG ; synchronisation AnkiWeb pour le téléphone.
- **P. 10 :** les greffons sont ensuite décrits comme **facultatifs**, mais le deck a été conçu avec eux ; essais annoncés sous **Anki 25.07.5 sur macOS**. Il faut conserver cette nuance entre le parcours d’installation recommandé et leur caractère facultatif.
- **P. 10–17 :** outils de surlignage et de tableaux, couleurs de l’éditeur, lecture de tableau ligne par ligne, recherche dans une carte, dessin temporaire, mode nuit, barre de révision, maintien du défilement, rythme de séance, couleurs des paquets, recherche rapide, export PDF et raccourci d’annulation.
- **P. 11 :** le **Propagateur de tableaux** peut recopier une correction vers des notes apparentées après accord de l’utilisateur. Le PDF indique que cette opération n’est pas annulable par Ctrl+Z. Ce n’est donc pas un simple effet visuel : une sauvegarde et une vérification des notes concernées s’imposent avant son utilisation.

Aucun greffon n’a été installé ou exécuté ; aucun paquet n’a été importé dans un profil Anki, fusionné ou corrigé pour cette lecture.

## Conséquences pour notre contrôle

1. **Identifier les ensembles séparément.** Ce document décrit MEA/Mohamed El Amri. L’identité avec Picat/C2SU et le mécanisme AnkiCollab ne sont pas établis dans ce PDF. Le document ne fournit pas non plus un canal de mise à jour automatique ni un historique d’éditions médicales par item.
2. **Auditer le paquet complet en lecture seule.** Conserver notes, GUID, types, tags et cartes, y compris `TOUR-doublon` et contenu C ; ne pas transformer le filtre de révision en suppression de preuves.
3. **Tester les 14 lacunes annoncées.** Rechercher notamment l’item 210, avec une correspondance source/notes explicitement confirmée. Distinguer déclaration de l’auteur, recherche automatique et constat validé par un humain.
4. **Comparer au référentiel identifié.** La mention « collège et LiSA » ne donne ni édition précise ni garantie d’actualité. Chaque objectif A/B doit avoir son repère source, ses notes, son constat, son relecteur et sa date.
5. **Reporter la fusion.** Aucune consigne de ce PDF n’autorise à assimiler ou fusionner les différentes distributions. Une comparaison des GUID, des champs, des types de notes et des versions reste nécessaire.

## Refaire la vérification

Télécharger le fichier depuis le lien exact ci-dessus ; contrôler son empreinte, puis lire **p. 8–9** pour le périmètre, le tag et les lacunes, **p. 9–10** pour l’installation, **p. 11** pour le propagateur. Vérifier aussi les exemples en images **p. 3–7**, absents d’une extraction textuelle seule. Si l’empreinte change, cette synthèse doit être confrontée à la nouvelle version.
