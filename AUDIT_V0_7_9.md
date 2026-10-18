# V0.7.9 — Assets et jeux de la taverne

Les trois jeux de la taverne (dés, pile ou face, pierre-feuille-ciseaux) disposent de tables bleues et dorées, de commandes interactives, de mises et d'animations reliées aux résultats du serveur.

Le choix des jeux réutilise les trois cartes illustrées du menu d'origine. La salle clandestine réutilise ses six boutons d'origine, avec leurs icônes. Le décor de chaque lieu reste visible derrière les menus. Les sélections sont cliquables au clavier et au toucher, avec un état de focus et des retours fonctionnels ; elles défilent sur les petits écrans.

Un nouvel atlas transparent fournit les deux faces de la pièce, le cadre des dés et les trois symboles indépendants de pierre-feuille-ciseaux. Les points du dé restent générés dynamiquement pour correspondre exactement à la valeur retournée par le serveur. Les menus ne sont pas de simples images avec un résultat figé. Les fonds de jeu bleus reprennent les couleurs des assets approuvés. Le nouvel atlas est encodé en WebP avec conservation de l'alpha ; son fichier et ses associations sont inclus dans le projet.

Correction : les noms français des gestes enregistrés par le serveur sont normalisés avant de sélectionner leur image. Cette association est couverte par un test automatique et par une comparaison de l'affichage avec l'état serveur en navigateur.

## Vérifications

- Compilation TypeScript et Vite réussie.
- 30 tests frontend et 28 tests API réussis ; compilation de tous les modules Python API/bot réussie.
- 16 parcours de régression des huit jeux en Chromium : ordinateur 1440 × 1000 et mobile 390 × 844, vrais clics, animations, verrouillage des commandes, résultats serveur, retours, absence de débordement horizontal et d'erreur JavaScript.
- Pendant la validation des nouveaux assets : 6 parcours supplémentaires des trois jeux de la taverne sur les deux formats, puis inspection des captures.
- Cadres et symboles isolés dans le navigateur ; suppression des fragments des cellules voisines et des fonds génériques autour des boutons d'origine.

Les essais ont utilisé une base locale dédiée avec des fonds de test. Aucun changement des règles, des gains ou de l'économie du serveur. Les essais n'ont pas été réalisés dans Brave ni dans l'Activity Discord intégrée. Cette version conserve les trois jeux solo contre le serveur ; les variantes contre un ami du visuel historique ne sont pas implémentées.

Livraison : anciens bundles de compilation retirés de l’archive ; seuls le script et la feuille de style référencés par la page sont conservés. Contrôle CRC et chargement du serveur, de la page, des bundles et des assets depuis une extraction neuve réussis.
