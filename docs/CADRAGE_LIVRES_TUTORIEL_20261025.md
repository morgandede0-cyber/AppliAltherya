# Livres et tutoriel : cadrage et assets

Mise à jour cumulative du 25 octobre 2026, à appliquer au projet existant puis reconstruire et redéployer.

Corrections :
- Les glyphes de statut du sommaire sont remplacés par trois assets SVG : terminé, quête en cours, cadenas. Leur affichage ne dépend plus des caractères disponibles dans la police.
- Le livre ouvert conserve ses proportions. La partie de l’image contenant les anciennes commandes est exclue du décor affiché, sans modifier l’asset original.
- Bibliothèque, navigation, compteur et lieux/preuves occupent un bandeau distinct. Les boutons utilisent l’asset commun du thème ; les flèches sont des formes indépendantes des polices.
- Livre et tutoriel utilisent un calcul commun de la fenêtre visible, du HUD et de la marge inférieure ; ils se redimensionnent avec la fenêtre.
- Le texte long reste défilable à l’intérieur des pages. Les informations, progression et récompenses restent celles du serveur.
- Le tutoriel reste uniquement explicatif, sans ouverture de menus et sans changement de récompense.
- Le bouton Quêtes de droite reste retiré.

Contrôles : compilation TypeScript/Vite, tests du journal et du guide, parcours des chroniques (bibliothèque, sommaire, pages, verrouillage, lieux/preuves, fermeture), contrôle des boutons dans la fenêtre sur 1440×900, 1186×570, 390×844 et 320×568. Le parcours du tutoriel vérifie les douze étapes, les bornes des boutons et la fin du contenu dans le cadre, la reprise et l’absence de seconde récompense.

Les captures de contrôle restent internes. Aucun changement de base de données, de prix ou de mécanique économique ; aucun déploiement public effectué.
