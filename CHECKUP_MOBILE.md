# Vérification mobile — 26 octobre 2026

## Corrections
- Le bouton principal de l’arène conserve sa position et les commandes ne se superposent plus ; les conseils et les résultats précédents restent consultables. Le temps d’attente défile dans le bouton du prochain combat.
- Les noms des techniques et leurs statistiques sont séparés. Les libellés des commandes de combat sont raccourcis à l’écran et leurs noms complets restent accessibles.
- La forge sépare les matériaux, leurs quantités et les conditions d’amélioration.
- Le marchand affiche ses cinq actions dans une grille adaptée au mobile et la taverne conserve ses accès dans le décor.
- La barre du joueur est décalée pour les contrôles Discord lorsque le jeu est ouvert comme Activity sur mobile.

## Vérifications locales
- Construction TypeScript/Vite réussie ; compilation Python réussie ; 261 tests de l’interface réussis.
- Tests en navigateur : quatre tailles de téléphone (320, 360, 390 et 414 px), interaction tactile et tailles de texte simulées à 135 % et 170 %. 132 contrôles de menus, achats, banque, forge, arène, contrats et retours réussis. Test supplémentaire du décompte, du nom « Enchaînement », des conseils et de l’historique.
- Quêtes et accès directs : 52 contrôles ; livres et barre : 120 ; tutoriel : 404 ; salle clandestine et jeux : 32 ; retour tactile du livre du troubadour : 6. Aucune erreur JavaScript ou ressource manquante observée lors de ces parcours. Audit des références d’assets : 220 contrôlées, aucune manquante.
- 601 tests serveur exécutés : 598 réussis au premier passage ; trois scénarios de test utilisaient l’ancien tutoriel ou l’ancien accès aux quêtes. Ces scénarios ont été actualisés et repassés avec succès, dont le contrôle anti-double récompense.

## Limites
Ces essais utilisent un navigateur et une base temporaires. La version réelle de Discord sur ton téléphone, le serveur Coolify de production et le partage de Gold avec Oddium n’ont pas été testés depuis cet environnement.

## Installation
Cette archive cumulative contient les assets et les mises à jour précédentes. Copie le contenu du dossier Altherya_V0_8_10 dans ton projet existant en remplaçant les fichiers correspondants, puis reconstruis et redéploie dans Coolify. Aucune remise à zéro ou modification des variables d’environnement n’est nécessaire.

## Vérifications complémentaires
- Commerce entre joueurs : 48 contrôles sur 2 formats PC et 2 formats mobiles. Les avatars Discord externes n'ont pas été validés dans cet environnement isolé.
- Tour d'Ashkar : 2 formats ; Popie : 24 contrôles ; Panda : 12 ; Smogo : 31 ; braquage : 10 ; métiers : 28.
- Port : 62 contrôles sur 4 formats jusqu'à la fin de l'enquête. Le test du port a été actualisé pour ne plus chercher un ancien bouton de quête ; la progression réelle de l'objectif est couverte séparément par les tests serveur.
- Blackjack : 32 contrôles ; roulette : 6 formats ; course : 4 formats, environ 9,8 à 9,9 secondes dans ces essais ; machine à sous : 24 contrôles, arrêt des rouleaux de gauche à droite ; dés : 4 formats.
- Tests de Smogo et des dés actualisés pour tenir compte de la limite actuelle et du retour vers la scène de jeux.
- Deux scripts anciens restent à adapter : celui du courrier cherche la recherche de joueurs sans ouvrir sa catégorie ; celui d'une quête cherche un ancien suivi latéral. Leur échec ne prouve pas un bug du jeu, mais ces parcours ne sont pas validés par ces scripts.
- Les tests navigateur utilisent Chromium et une base temporaire ; ils ne remplacent pas un essai sur les appareils et comptes Discord réels. Le serveur Coolify, les vrais avatars Discord et la base Gold partagée avec Oddium ne sont pas accessibles pour ces essais.
