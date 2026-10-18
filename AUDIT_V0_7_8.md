# V0.7.8 — Jeux interactifs et catalogue graphique

Les huit jeux utilisent maintenant des éléments interactifs dans le navigateur. Les résultats et les soldes proviennent toujours du serveur ; les animations présentent le résultat reçu et ne calculent pas de gains supplémentaires.

- Black Jack : distribution, cartes cliquables, carte cachée, tirer/rester, total et résultat.
- Roulette : 37 secteurs, choix du numéro ou des chances simples, rotation de la roue et de la bille, arrêt sur le numéro serveur.
- Machine à sous : trois rouleaux animés avec arrêts successifs et les cinq symboles du serveur.
- Courses : quatre chevaux animés sur des pistes distinctes, choix du cheval et cotes réelles, arrivée conforme au serveur.
- Roulette russe : barillet stylisé à six chambres animé, étapes et état du jeu.
- Dés, pile ou face, pierre-feuille-ciseaux : choix interactifs, animations puis résultat.

Les commandes sont verrouillées pendant une requête et son animation. Les mises non entières, nulles ou trop élevées sont refusées. Une partie active peut être reprise ; l'interface empêche de lancer un autre jeu tant qu'elle est en cours. Les animations sont annulées à la fermeture et respectent la préférence de mouvement réduit.

La forge et le marchand adoptent les visuels approuvés. Textes, prix, stocks, matériaux et paliers sont générés depuis l'état du serveur. Le marchand conserve quatre objets au maximum par page, une catégorie histoire indépendante et une confirmation d'achat/vente. Les anciens boutons du marché sont masqués lorsque la boutique est ouverte. Les images des vingt paliers d'équipement et le catalogue de ressources sont intégrés ; les commandes graphiques supplémentaires restent disponibles pour les futurs écrans.

## Validation effectuée

- Compilation TypeScript et production Vite : réussies.
- `cd apps/game && npm test` : 29 tests réussis.
- `python3 -m unittest discover -s apps/api/tests` : 28 tests réussis.
- Navigateur Chromium, 1440 × 1000 et 390 × 844 : les huit jeux, soit 16 parcours, animations actives, commandes verrouillées, résultats et absence de débordement horizontal ; aucune erreur JavaScript.
- Navigateur : 4 parcours commerce/forge sur les deux formats, achats avec annulation et confirmation, rupture de stock, vente de trois unités, amélioration et changement d'outil ; aucune erreur JavaScript.
- Captures des jeux, du marchand et de la forge inspectées ; correction d'une collision CSS sur pile ou face, du placement du titre et des équipements, et de la hauteur mobile.

Les essais utilisent une base SQLite locale dédiée et des fonds de test. Pas de mise en production, ni de test dans Brave ou l'Activity Discord intégrée pendant cette vérification. Sur petit écran, les tables longues restent défilables. Les modifications portent sur le client et les assets, pas sur les règles ou l'économie du serveur.
