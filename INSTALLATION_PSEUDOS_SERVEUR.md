# Surnoms du serveur Discord

## Ce qui change

Le jeu affiche désormais en priorité le **surnom défini sur votre serveur Discord**. S’il n’y en a pas, il utilise le nom d’affichage global du compte, puis son nom d’utilisateur Discord.

Le choix s’applique aux profils, HUD, classements, recherche admin, noms visibles des combattants, nouveaux logs et prochaines Gazettes. Les sessions et la liste des tutoriels terminés utilisent le même nom. Les messages déjà envoyés et les anciens textes de combat ne sont pas réécrits.

## Installation

1. Mettre les fichiers du correctif dans le projet **Menu Portail V2** précédent, ou utiliser l’archive complète.
2. Mettre à jour GitHub puis reconstruire/redéployer le service Activity sur Coolify.
3. Conserver `DISCORD_BOT_TOKEN` en runtime, les variables OAuth et le volume `ACTIVITY_DB` existants. Le bot doit être dans le serveur et pouvoir voir le salon portail.
4. Fermer puis relancer l’Activity depuis Discord : le surnom est demandé pendant la connexion. Les joueurs déjà enregistrés sont aussi actualisés progressivement en arrière-plan.

Aucune nouvelle permission OAuth, scope utilisateur ou variable VITE n’est ajoutée. Il n’est pas nécessaire d’activer l’intent privilégié Server Members : le code lit un membre précis via REST et ne liste pas tout le serveur.

## Quel serveur est utilisé ?

Le serveur est déterminé côté API à partir du salon portail `1551927225253761044`, ou de `ALTHERYA_PORTAL_CHANNEL_ID` si configuré. L’ID de serveur n’est jamais accepté depuis le navigateur. Le bot récupère lui-même le serveur du salon Discord.

Facultativement, `DISCORD_GUILD_ID` peut fixer directement l’ID de votre serveur. Cette variable désigne le **serveur**, pas l’application ni le salon. Elle n’est pas nécessaire avec le salon portail actuel.

## Mise à jour et secours

La connexion force une lecture du surnom. En arrière-plan, seuls les comptes déjà connus du jeu sont traités : aucun import de tous les membres Discord dans la liste admin. Le worker traite environ un joueur par seconde ; chaque profil devient rééligible après cinq minutes. Sur une grande liste, le délai dépend du nombre de joueurs et des limites Discord. L’interface récupère ensuite les nouvelles données avec son actualisation habituelle (environ quinze secondes), ou lors de la réouverture d’un menu.

Si le surnom est retiré, une lecture Discord réussie rétablit le nom global/username. Si le membre ne fait plus partie du serveur (404 confirmé), l’ancien surnom est retiré. Si Discord est indisponible ou refuse la lecture, le dernier surnom vérifié du même serveur reste utilisé ; sans cache, le nom du compte sert de secours. La connexion au jeu continue de fonctionner.

Un token absent ou un refus 401/403 est signalé dans les logs Coolify, sans afficher de secret. Les 429 déclenchent une pause conforme au délai Discord. Le worker ne modifie jamais un pseudo sur Discord : il ne fait que lire les noms et les afficher dans le jeu.

## Données conservées

Les ID Discord restent les clés des comptes et des autorisations. Un surnom ressemblant au nom ou à l’ID d’un admin ne donne aucun droit. Aucun changement de Gold, XP, inventaire, tutoriel ou récompense. Les avatars de compte restent inchangés. Les noms des profils canoniques sont actualisés, sans recréer les personnages.

L’économie est toujours la SQLite isolée de l’Activity ; cette modification ne connecte pas Oddium/PostgreSQL. Les menus et assets approuvés du projet sont conservés.
