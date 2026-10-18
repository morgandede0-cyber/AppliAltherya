# Nouveau profil du joueur

Le bouton Mon profil et les raccourcis existants ouvrent un profil dans le style du
Journal d’Altherya : cadre en bois, fond bleu sombre, portrait, niveau et XP,
portefeuille et banque, équipement, parcours et réputations. Les outils absents
sont indiqués Non possédé. Les barres de réputation représentent le rang atteint
sur cinq, pas une progression inventée entre deux rangs.

Le nom affiché vient de la session serveur vérifiée : surnom du serveur Discord,
sinon nom Discord de secours. Le service de surnoms existant nécessite le token
du bot et son accès au serveur ; DISCORD_GUILD_ID peut préciser le serveur cible.
L’avatar passe par le proxy /api/avatar existant. En cas d’échec, des initiales
restent affichées. Aucun nom ni avatar de démonstration n’est inclus dans le jeu.

Les données se mettent à jour lors de l’actualisation habituelle (environ 15 s).
L’inventaire conserve la catégorie et la page pendant ces actualisations. Les
ressources et objets d’histoire restent séparés ; quatre objets maximum par page.
Les chapitres connus par le catalogue sont indiqués sur les objets d’histoire.

Installer l’archive complète dans le dépôt GitHub, ou extraire le correctif léger
à la racine du projet existant qui contient apps/, puis redéployer sur Coolify.
Le correctif inclut aussi le Journal des mises à jour précédent et son cadre.
Conserver les variables de déploiement et le volume de données. Aucun reset,
changement de prix ou de récompense n’est prévu. Aucun déploiement distant n’a été effectué.
