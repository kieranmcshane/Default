# Installer le Deck EDN - MEA

Source : « LISEZ-MOI anki.pdf » de Mohamed El Amri, dans le dossier Drive fourni
(`1w3NoLnODfW1L69wGdNmbTrWEJHCyuOIR`). Instructions testées par l'auteur sur Anki 25.07.5 (macOS).

> L'ordre compte : installer les add-ons **avant** d'importer le paquet.

## 1. Installer Anki sur ordinateur

Version **25.07 ou plus récente** : <https://apps.ankiweb.net>.

## 2. Installer les add-ons

1. Dans Anki : **Outils → Modules complémentaires → Obtenir des modules**.
2. Coller tous les codes d'un coup, séparés par des espaces :

   ```
   2058761538 1152511019 1095027583 1359741508 582574510 337419702 1279903969 1343483268 469090413 415651412 1867552527 1990351838 1902100219 523876668 1721258263 1136455830
   ```

3. Valider, puis **redémarrer Anki**.

Ils sont facultatifs mais le deck a été pensé avec eux. Ils ne touchent pas au planning des
cartes et ne changent que l'affichage, sauf le **Propagateur de tableaux** (1095027583), qui
recopie une correction de tableau vers les cartes sœurs après accord (non annulable par Ctrl+Z).

| Add-on | Code | Rôle |
|---|---|---|
| Ancre Lumière (surligneurs) | 2058761538 | 17 boutons de mise en forme dans l'éditeur |
| Outils tableau | 1152511019 | insère un tableau au format du deck |
| Propagateur de tableaux | 1095027583 | corrige un tableau partagé sur toutes ses cartes |
| Éditeur : couleurs Format MEA | 1359741508 | affiche les couleurs du deck dans l'éditeur |
| Sweep | 582574510 | révèle un tableau ligne par ligne (touche `s`) |
| Cmd+F dans la carte | 337419702 | recherche dans la carte affichée |
| Dessin sur la carte | 1279903969 | calque de dessin éphémère (touche `c`) |
| Mode nuit | 1343483268 | mode nuit qui garde les surlignages (touche `N`) |
| Barre du bas Format MEA | 469090413 | style des boutons de réponse ; **nécessite** Advanced Review Bottom Bar (1136455830) |
| Pas de défilement automatique | 415651412 | la carte reste en place à l'affichage de la réponse |
| Session Pace Tracker | 1867552527 | rythme de la séance (objectif 800 cartes, 6/min par défaut) |
| Couleurs des paquets | 1990351838 | une couleur par matière |
| Deck Quick Search | 1902100219 | ouvrir un paquet au clavier (Ctrl+Y) |
| Export PDF des cartes | 523876668 | exporte un paquet en PDF |
| Force Ctrl+Z | 1721258263 | force le raccourci Annuler |
| Advanced Review Bottom Bar (autre auteur) | 1136455830 | requis par la barre du bas |

Réglage d'un add-on : Outils → Modules complémentaires → le sélectionner → **Configuration**.

## 3. Importer le paquet

Télécharger `Deck EDN - MEA.apkg` (1,6 Go) depuis le Drive, puis double-cliquer dessus
ou **Fichier → Importer**.

## 4. Téléphone

Synchroniser avec AnkiWeb depuis l'ordinateur, puis depuis le téléphone. Le paquet marche
partout ; les add-ons seulement sur ordinateur.

## 5. Deck allégé (facultatif)

Les notes redondantes portent le tag `TOUR-doublon` (rien n'est supprimé). Pour réviser sans
elles, créer un paquet filtré (**Outils → Créer un paquet filtré**) avec la recherche :

```
deck:"Deck EDN - MEA" -tag:TOUR-doublon
```

≈ 26 800 cartes au lieu de ≈ 42 800. Une seule matière :
`deck:"Deck EDN - MEA::CARDIOLOGIE" -tag:TOUR-doublon`.

## Avant d'appliquer nos corrections

Les corrections de `audit/` désignent les notes par leur identifiant : dans le navigateur
d'Anki, rechercher `nid:1780590545604`. Modifier une note existante conserve son historique
de révision ; ne pas supprimer et recréer.
