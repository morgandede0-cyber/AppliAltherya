# Carnet d’aventurier — 24 octobre 2026

Les huit rubriques Métier, Voyage, Entraînement, Défis, Recherches, Forge, Titres et Confort utilisent désormais un habillage cohérent avec les interfaces récentes : fond encre, titres chauds, bordures discrètes, boutons lisibles et fermeture toujours accessible.

Navigation latérale sur ordinateur, huit onglets répartis sur deux lignes sur mobile. Le contenu défile indépendamment du cadre. Métiers et outils affichent une sélection à la fois. Les choix définitifs de spécialisation et le remplacement quotidien disposent d’une confirmation dédiée. Recherche, sélection et position sont conservées lors des actualisations ; un changement de compte retire immédiatement les informations privées.

Les données restent celles du serveur : maîtrise, rencontres, défis, recettes, matériaux, titres et entraînement. Les règles, prix, récompenses et sauvegardes ne sont pas modifiés. Les illustrations réutilisent les ressources du projet. Aucune modification de backend en production ; une assertion de test ancienne a été ajustée pour accepter les métadonnées des quêtes ajoutées précédemment, tout en vérifiant le catalogue d’origine.

Validation : compilation de production, 223 tests d’interface, 15 tests serveur du carnet et compilation Python. Les parcours navigateur utilisent le jeu et l’API réels avec une base temporaire, sans compte Discord réel ni modification de données de production. 105 contrôles navigateur passent sur 1440×900, 1186×570, 825×1150, 390×844 et 320×568, sans erreur JavaScript. Ils couvrent la géométrie des huit rubriques, la spécialisation, la rencontre, les favoris, le suivi de forge, le remplacement quotidien (ou son refus si aucun autre défi n’est disponible), le titre, l’entraînement sans récompense et les préférences locales. Voir browser-adventure-redesign.cjs.

Cette archive est une mise à jour cumulative à superposer au projet existant. Elle conserve les correctifs et assets des livraisons précédentes ; elle ne contient pas la bibliothèque complète des anciens décors. Aucun déploiement n’a été effectué.
