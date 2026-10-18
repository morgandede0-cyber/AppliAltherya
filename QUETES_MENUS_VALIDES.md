# Menus de quêtes intégrés

Les deux panneaux reprennent le visuel choisi : bois sombre, or antique, fond bleu pétrole, soleil pour les quêtes quotidiennes et boussole pour l’histoire.

À gauche : les défis actuels du serveur, leurs icônes, leurs compteurs et barres de progression, les coches de réussite, la récompense réelle en Gold/XP et un bouton de récupération direct. Le bouton est désactivé tant que tous les objectifs ne sont pas terminés, pendant la requête et après récupération.

À droite : saison, chapitre, titre et étapes de la campagne actuelle. L’étape en cours est dorée ; les étapes terminées sont cochées. Le bouton Voir les détails ouvre les interactions existantes de la campagne. Les accès Chroniques, Missions et Objectifs sont conservés.

Les noms et objectifs illustratifs de l’aperçu ne remplacent pas le scénario. Les quêtes et récompenses réelles restent gérées par le serveur. Le tirage quotidien, les restrictions de lieux, l’économie et la progression ne sont pas modifiés.

Les panneaux se replient et conservent le réglage existant du navigateur. Sur petit écran, ils démarrent repliés et un seul peut être ouvert à la fois. Les cadres sont assemblés en sections pour préserver la forme des médaillons et des ornements ; le contenu long défile à l’intérieur.

## Installer la mise à jour seule
Extraire Altherya_Quetes_Menus_Valides.zip. Copier son dossier apps et ses fichiers de documentation dans la racine du projet existant, en remplaçant les fichiers concernés. Envoyer les changements sur GitHub et redéployer sur Coolify. Le Dockerfile existant recompile les sources.

Le projet complet contient déjà la mise à jour. En local : cd apps/game, npm ci, npm run build. La mise à jour n’inclut ni vos variables .env ni vos données de serveur.
