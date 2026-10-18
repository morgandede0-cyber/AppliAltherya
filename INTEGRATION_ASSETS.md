# Intégration des menus — 10 octobre 2026

## Installation
Extraire le correctif à la racine du projet (le dossier qui contient apps), remplacer les fichiers, puis utiliser votre procédure habituelle de mise à jour GitHub et redéployer sur Coolify. Le projet complet est également fourni. Aucune migration ni remise à zéro des données n'est nécessaire.

## Corrections
- Marché : une seule scène, quatre boutons d'origine. Suppression de la deuxième image du marchand et du cadre Boutique obsolète, y compris sur mobile.
- Achats/ventes : cadres, médaillons et boutons graphiques du marchand, valeurs réelles, quatre objets maximum par page. Les objets d'histoire restent séparés et identifiés par chapitre.
- Forge : illustration liée à l'outil réellement possédé, aperçu de l'amélioration et coûts placés dans les emplacements natifs.
- Banque : montants et commandes dans les cadres d'origine ; valeurs sur une ligne sur mobile.
- Expéditions : retrait des illustrations et textes d'exemple, informations réelles replacées dans les bandeaux ; accessoires indisponibles clairement présentés.
- Petites annonces : sceaux de rareté des assets, mission et récompense réelles, contrat interactif conservé.
- Matériaux : les zones variables reprennent les textures des assets au lieu de grands aplats étirés. Le hub garde ses boutons d'origine.

## Validation effectuée
- Compilation TypeScript et build Vite réussis.
- 34 tests du client et 36 tests API réussis.
- 99 contrôles de menus via navigation réelle, sur 1440×900, 1186×570 et 390×844 : bornes des menus, achats, amélioration, dépôt/retrait, parcours ; aucune erreur JavaScript ni requête d'asset en échec.
- 20 contrôles des jeux animés réussis.
- Revue des captures du marché, forge, banque, annonces et préparation des expéditions.

Les actions serveur ont été testées sur une base SQLite temporaire et isolée. La connexion à l'économie du serveur de production n'a pas été validée pendant cette correction visuelle. Aucun fichier de serveur ni de base de données de production n'a été modifié.

Test des menus : après npm run build dans apps/game, exécuter node tests/browser-menu-assets.cjs avec Playwright/Chromium disponibles. Les captures sont écrites dans SCREENSHOTS_DIR si défini.
