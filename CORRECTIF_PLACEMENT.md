# Correctif du placement des menus — 11 octobre 2026

## Installation
Ouvrir le dossier du dépôt contenant `Dockerfile` et `apps/`. Copier dedans le contenu du dossier `Altherya_V0_8_10` de cette archive et accepter le remplacement des fichiers. Envoyer la mise à jour sur GitHub, puis redéployer dans Coolify. La compilation du frontend est faite par le Dockerfile. Recharger ensuite l’Activity pour charger cette version.

Deux archives peuvent être utilisées : le projet complet, ou le correctif léger contenant uniquement les fichiers modifiés. Le correctif léger s’applique à la version avec les menus adaptés livrée précédemment.

## Placement corrigé
- Un même calcul de largeur, hauteur disponible et centrage pour les menus illustrés, les jeux, le profil, le livre et la carte.
- Espace réservé sous la barre d’informations, adaptation à la fenêtre réelle et défilement vertical sur les petits écrans.
- Les coordonnées des zones cliquables et des textes suivent l’image de leur menu ; les anciens décalages CSS ne peuvent plus les déplacer.
- Le seuil PC/mobile est cohérent à 600 pixels, y compris à 600 exactement et lors des redimensionnements.
- Un nouveau menu commence en haut ; une mise à jour du même menu conserve le défilement. Les mises à jour ne déplacent plus le focus.
- Textes et grands montants ajustés dans leurs zones, sans dépasser les cadres.
- Recomposition mobile du marchand, du tableau de bord, de l’arène, des techniques et de la forge avec des cadres mieux délimités.
- Forge : matériaux affichés sur des lignes lisibles dans un cadre composé à partir de l’asset ; prix et niveau recalés ; boutons du bas séparés sur mobile.
- Combat : noms/PV dans les plaques, barres de vie dans leurs rails, logs dans le cadre central, libellés centrés dans les boutons.
- Techniques : suppression des textes en double sur les titres graphiques ; puissance/recharge et utilisation dans les emplacements vierges.
- Carte complète ajustée à la fenêtre, accès et retour placés sur la carte.
- Les fenêtres de confirmation récupèrent le placement du menu à leur fermeture.

## Contrôles
Compilation TypeScript/Vite et 34 tests frontend réussis. Compilation Python et 36 tests API réussis. Vérifications navigateur : 99 vues de menus sur PC, écran court et mobile ; 20 contrôles des jeux et animations ; 38 contrôles de fenêtres/retours ; 36 vues avec achats, forge, profil, carte et livre ; 10 contrôles de braquage. Les 16 contrôles du nouveau test de placement couvrent les tailles 390, 600, 601, 768, 1024 et 1440 pixels, les limites de fenêtre, les ancrages du tableau de bord, les matériaux, la carte complète, le combat et les techniques.

Les captures utilisées pour la revue sont internes. Les tests utilisent une base SQLite temporaire. Le serveur Coolify, la connexion Discord réelle et le Gold partagé en production ne sont pas accessibles dans cet environnement et ne sont pas présentés comme testés. Les fichiers API, l’économie, les données et le hub central restent ceux de l’archive de départ.
