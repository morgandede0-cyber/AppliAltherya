# V0.7.3 — suppression des anciens boutons d’interaction

- Anciennes zones et petits boutons des PNJ supprimés des décors : tavernier, jeux, troubadour, forgeron, château, arène, banque, ruelle, vigile, voleur, braqueur, casino et expéditions.
- Le menu « Actions du lieu » et le bouton « ← Revenir » ont été retirés du HTML et de leurs gestionnaires.
- Le hub et les quatre actions modernes du marché (Histoire, Acheter, Vendre, Partir) sont conservés.
- Les lieux ouvrent directement leur menu. Le troubadour ouvre son livre, Elarwyn/Vorak ouvrent la préparation adaptée à leur destination. Fermer un menu de lieu ramène au lieu parent et ouvre son menu, sans décor dépourvu d’actions.
- Gestionnaires d’interactions devenus inutiles supprimés ; graphe de navigation adapté aux menus actuels.

Validation : build TypeScript/Vite réussi ; 28 tests TypeScript et 28 tests API Python réussis ; compilation des modules Python de apps/api et apps/bot. Parcours Chromium PC (1440×1000) et mobile (390×844) : 24 vérifications de suppression et navigation sans erreur JavaScript/HTTP, plus ouverture/fermeture de la boutique et présence de ses quatre actions. Aucun bouton ancien ne subsiste dans les scènes concernées, y compris après fermeture du menu.

Les changements visuels de V0.7.2 et le parchemin des annonces sont conservés. Aucun changement d’économie ou de base de données : l’économie locale de test reste séparée du Gold partagé Oddium. Brave et Discord n’ont pas été testés directement. Les limites fonctionnelles indiquées dans AUDIT_V0_7_2.md restent inchangées.
