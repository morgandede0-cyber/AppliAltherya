# Château — version intégrée

Les trois écrans sont fonctionnels : accueil du château, tableau de bord personnel et podium.

L’accueil reprend les trois illustrations du modèle approuvé. Les titres et commandes sont de vrais éléments interactifs. Le cadre vide et les piédestaux permettent d’afficher les données actuelles sans conserver des montants fictifs dans les images.

Le tableau de bord utilise le surnom serveur et la photo Discord disponibles, l’expérience, les activités, les réputations, les chapitres, l’expédition, le contrat, les soldes et les quêtes quotidiennes. Le podium utilise les surnoms, photos et fortunes transmis par le serveur. Aucune place personnelle n’est inventée : le bandeau affiche la fortune réelle du joueur.

Les informations sont mises à jour par l’actualisation existante du jeu et par le bouton Actualiser. La récompense quotidienne se désactive après attribution ; les requêtes sont bloquées pendant une opération. En cas d’absence de photo, les initiales sont utilisées.

Sur téléphone, les accès et piédestaux passent en colonne avec défilement à l’intérieur du cadre ; les commandes de retour restent accessibles en bas.

## Installation de la mise à jour seule
1. Extraire Altherya_Chateau_Final.zip.
2. Copier son dossier apps et ses fichiers de documentation dans la racine du projet existant, en acceptant le remplacement des fichiers correspondants.
3. Envoyer les changements sur GitHub puis redéployer dans Coolify. Le Dockerfile existant recompile le jeu. Pour un lancement local : cd apps/game, npm ci, npm run build.

Le projet complet contient déjà ces modifications. Les bases de données et fichiers .env de votre hébergement ne sont pas inclus dans cette mise à jour.
