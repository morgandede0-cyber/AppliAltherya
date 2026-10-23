# Panda — maître du Port des Brumes

Panda remplace le personnage de la capitainerie. C’est un panda massif en uniforme de capitaine. Sa grosse matraque en bambou repose sur le bureau ; elle fait partie du décor et n’ajoute pas d’arme à l’inventaire.

La scène existante `apps/game/public/assets/port/capitainerie.png` est remplacée. La composition, le bureau et la vue du port sont conservés. L’image est chargée avec une nouvelle référence de cache pour éviter d’afficher l’ancien personnage après mise à jour.

L’action accessible porte le nom « Parler à Panda ». Les dialogues et l’objectif de remise du dossier utilisent son nom. La clé interne `captain`, les objectifs, les indices, le combat, les choix d’intervention et les récompenses restent compatibles avec les sauvegardes existantes. Les anciens dialogues mémorisés sont renommés à l’affichage, sans effacer la progression.

Accès : Monde → Port des Brumes → Capitainerie. Le port conserve son déblocage par l’histoire principale.

Consignes artistiques : `docs/panda-prompts.json`. Génération intégrée puis édition de la même scène pour ajouter la matraque. Aucune modification des tarifs des outils ou du bonus du tutoriel. Aucun déploiement sur le serveur réel.
