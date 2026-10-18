# Installation

Le correctif s’applique à la dernière version « Altherya_Tutoriel_Restaure » (version 20). Copiez le contenu du dossier Altherya_V0_8_10 dans votre projet et acceptez les remplacements. Appliquez ensemble les fichiers du jeu et ceux de l’API. Le projet complet comprend aussi les assets existants.

Conservez vos fichiers .env et votre base de données. Aucune nouvelle variable d’environnement n’est nécessaire : les tables du tutoriel sont créées automatiquement au démarrage. Le chemin ACTIVITY_DB doit continuer à pointer vers votre base sur un volume persistant ; une base éphémère perdrait la progression au redéploiement.

Publiez via votre procédure GitHub habituelle puis redéployez le service dans Coolify. Pour construire localement : npm ci puis npm run build dans apps/game. Vérifiez ensuite le premier parcours, le retour au hub, un rechargement et la relecture depuis le profil. Ne remplacez pas votre base par une base de test.

Pour le service Discord, conservez DISCORD_CLIENT_ID, DISCORD_CLIENT_SECRET et la configuration frontend VITE_DISCORD_CLIENT_ID habituelle. Si les variables OAuth serveur sont présentes, la connexion vérifiée est obligatoire avant le tutoriel. N’effacez pas ACTIVITY_DB : ce fichier contient aussi la liste permanente des récompenses. Les nouvelles tables et la migration des sessions sont automatiques. Faites une sauvegarde de la base avant le redéploiement.

Après déploiement, testez avec un nouveau compte : tutoriel obligatoire, reprise après fermeture, récompense unique. Reconnectez ensuite le même compte dans un autre navigateur : il doit retrouver son profil et aucun second gain. Les illustrations proposées séparément ne remplacent pas les menus dans cette livraison.
