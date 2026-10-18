# Menus adaptés — 11 octobre 2026

Les menus vierges approuvés sont intégrés avec des informations réelles et des contrôles interactifs. Les soldes, stocks, coûts, niveaux, états de combat et résultats restent calculés par le serveur.

## Changements
- Marché : illustration propre avec quatre emplacements par page ; outils et ressources séparés des objets d’histoire ; chapitre indiqué ; achats/ventes avec confirmation, quantité et actualisation.
- Forge : images des équipements actuels et suivants, recettes, matériaux, niveau et coût placés dans les cadres originaux.
- Banque : soldes et montants dans les emplacements natifs ; sur mobile, dépôt et retrait séparés, retour après les formulaires.
- Taverne, château, arène, techniques, ruelle, casino et expéditions : zones cliquables alignées avec les assets, adaptation à la largeur de l’écran et textes ajustés.
- Jeux : cartes, roulette, rouleaux, chevaux et barillet animés ; mises, résultats et actions dynamiques. Les libellés variables ont été retirés des illustrations pour éviter les doublons.
- Fenêtres : une seule fenêtre active, retour/Echap, boutons bloqués durant les requêtes et messages visibles dans la fenêtre concernée.
- Les sprites de cartes et chevaux originaux sont conservés séparément des fonds vierges.

## Validation
- Compilation TypeScript/Vite réussie.
- 34 tests frontend réussis.
- 36 tests API réussis, compilation Python réussie.
- 99 vérifications des menus sur 1440×900, 1186×570 et 390×844 ; aucun asset manquant ni erreur JavaScript.
- 20 vérifications des huit jeux, animations et résultats sur ordinateur/mobile.
- 10 vérifications des braquages : essais, reprise, panne réseau et récompense.
- 38 vérifications des couches, confirmations, retours, fenêtres uniques et transitions.
- Captures internes inspectées : forge, marché, banque, boissons et jeux.

Les tests utilisent une base SQLite temporaire. Le déploiement Coolify, la connexion Discord réelle et la base de production ne sont pas vérifiés depuis cet environnement.

## Mise à jour
Remplacer les fichiers du projet dans le dépôt GitHub, lancer votre procédure habituelle de mise à jour puis redéployer dans Coolify. Garder vos variables d’environnement et votre volume de données actuels. La modification porte sur les interfaces ; elle ne migre pas l’économie.

## Provenance des retouches graphiques
Retouches avec ImageGen à partir des assets existants, puis conversion WebP sans perte :
- Forge : effacer uniquement les données figées dans le cadre des matériaux ; préserver les ornements, titres et dimensions.
- Marchand : vider les quatre cartes de produits et leurs valeurs pour les alimenter par le code ; préserver cadres, catégories et boutons.
- Blackjack, courses, machine à sous et roulette russe : effacer uniquement les libellés des actions qui changent pendant la partie ; préserver boutons et scènes.
- Roulette : effacer les numéros figés et les libellés variables ; conserver le mécanisme et les cadres. Les numéros exacts et la rotation sont dessinés par le code.

Les fichiers importants sont dans apps/game/src/ui/{commerce,native-games,artwork-layout,native-menus,illustrated,refined-menus,live-games,menu-layout} et apps/game/public/assets. Le Dockerfile compile le frontend au déploiement ; les dépendances et les bases de test ne sont pas incluses dans l’archive.
