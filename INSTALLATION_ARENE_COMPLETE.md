# Arène : champions, combat et résultats

## Ce qui change

Les dix champions conservent leurs noms, statistiques et techniques. Chacun a désormais un enchaînement ou une réaction identifiable. Doran (V) et Asterion (X) passent une seule fois en seconde phase sous 50 % PV : leur prochaine attaque reçoit respectivement +10 % et +20 % de puissance. L’intention affichée est l’action réellement prévue pour le prochain tour adverse ; sa résolution reste soumise aux règles de précision, garde et effets du moteur.

L’écran de combat rassemble PV, états, manche, phase, intention adverse, quatre techniques, recharge et journal des dernières actions. Les pertes de PV et impacts sont animés, avec respect du réglage de réduction des animations. Les boutons sont verrouillés pendant la résolution ; l’abandon demande confirmation. Le combat peut être replié puis repris depuis l’arène.

Le résultat présente victoire, défaite ou abandon, mise, versement brut, bénéfice ou perte nets, XP réellement reçue, classement, durée, manches, PV restants, statistiques des deux combattants et prochain champion. L’arène affiche les derniers résultats et permet de rouvrir le dernier rapport, même après un autre jeu. Cette consultation ne rejoue ni le règlement ni la récompense.

## Installation

1. Faire une sauvegarde de la base persistante avant mise à jour.
2. Extraire le correctif à la racine du dépôt et remplacer les fichiers correspondants. Le ZIP complet contient le dossier racine `Altherya_V0_8_10` : copier son contenu dans le dépôt si vous utilisez cette version.
3. Envoyer les fichiers sur GitHub avec votre méthode habituelle, puis redéployer dans Coolify. Le Dockerfile existant reconstruit le frontend.
4. Conserver le volume de données existant et la configuration `ACTIVITY_DB` pointant sur la même base dans `/app/data`. Aucun reset ni nouvelle variable n’est requis.
5. Ouvrir Arène, consulter Mes techniques, puis lancer un défi. Vérifier le bilan et Dernier résultat après retour au menu.

La nouvelle table `activity_arena_results` est créée automatiquement. Les cinq derniers rapports sont exposés par joueur ; les rapports restent conservés dans la base. Aucun ancien combat terminé ne reçoit de statistiques inventées. Le mécanisme existant de remboursement unique des parties interrompues au redémarrage est conservé.

## Économie conservée

La récompense du tutoriel reste 100 Gold et 25 XP, une seule fois. Les outils et le sac restent à 400 Gold. Les prix de forge, récompenses de campagne et quotidiennes, règles de mise (0 à 500 Gold), gains, XP, classement et délai de l’arène ne sont pas modifiés par cette mise à jour. Le correctif inclut aussi les fichiers nécessaires des précédentes corrections d’économie et de sauvegarde.

Cette version utilise la base SQLite persistante de l’Activity. Elle ne fournit pas de connexion à une économie distante Oddium. La validation locale ne constitue pas un déploiement sur le serveur Discord.
