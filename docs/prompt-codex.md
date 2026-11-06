# Prompt pour Codex — audit d'un lot de pneumologie

Copier-coller tel quel dans Codex, en changeant seulement la lettre du lot (A à F, voir
`audit/TACHES.md`). Un lot par tâche ; plusieurs tâches peuvent tourner en parallèle.

---

```
LOT : A

Dépôt kieranmcshane/Default. Ta tâche : auditer les items du lot ci-dessus, listés dans
audit/TACHES.md (phase 1), en suivant audit/PROTOCOLE.md à la lettre. Ce travail sert à
corriger des cartes de révision médicales : l'exactitude prime sur la vitesse.

Avant de commencer :
1. Pars de main à jour. Vérifie que audit/PROTOCOLE.md, audit/TACHES.md et
   outils/valider_audit.py existent ; sinon arrête-toi et dis-le.
2. Crée la branche codex/audit-pneumo-lot-<LOT>.
3. Exécute l'étape 0 du protocole. Si un téléchargement échoue, si une empreinte SHA-256
   diffère ou si les objectifs recalculés diffèrent de references/cep9/objectifs.csv :
   arrête-toi, ne produis aucun audit, rapporte la sortie exacte des commandes.

Pour chaque item du lot, l'un après l'autre :
- Étape 1 : génère local/travail/item-<ITEM>.txt et lis-le EN ENTIER (contenu A/B du CEP 9e,
  puis toutes les notes du deck). Pas de survol par mots-clés.
- Étapes 2 et 3 : écris audit/pneumologie/item-<ITEM>.csv (une ligne par objectif officiel
  A/B) et item-<ITEM>-corrections.csv. Les fichiers item-204, item-205 et item-360 sont les
  modèles du niveau de détail attendu.
- Étape 4 : « python outils/valider_audit.py <ITEM> » doit afficher 0 erreur ; lis les
  avertissements. Puis un commit pour cet item seul.

Interdit :
- modifier autre chose que audit/pneumologie/item-<ITEM>*.csv (ni outils/, ni references/,
  ni les README, ni TACHES.md) ; si un outil semble faux, signale-le au lieu de le corriger ;
- recopier le texte du référentiel ou des cartes : le dépôt est public, reformule ;
- inventer un fait, un chiffre, un numéro d'item ou un identifiant de note : tout doit
  venir des fichiers de local/ ;
- proposer de supprimer ou de suspendre une carte ; tenir compte du rang C ;
- remplir relu_par et relu_le (réservés au relecteur humain).
En cas de doute : statut le plus prudent et « à confirmer par un humain » dans le constat.

À la fin : pousse la branche et ouvre une pull request vers main intitulée
« Audit pneumologie — lot <LOT> ». Dans la description : le rapport de l'étape 5 du
protocole et la sortie complète de « python outils/valider_audit.py <ITEMS du lot> ».
Ne fusionne pas la pull request.
```
