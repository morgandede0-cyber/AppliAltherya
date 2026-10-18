# Techniques dérobées aux champions

## Fonctionnement

Chaque première victoire contre un champion débloque sa technique, définitivement et sans tirage aléatoire. La technique apparaît sur le bilan. Le rattrapage automatique des anciennes victoires est supprimé. Au premier démarrage de cette mise à jour, tous les joueurs repartent du champion I, avec leur collection et leur équipement de techniques vidés. Ce reset unique ne se répète pas aux redémarrages suivants. Seules de nouvelles victoires débloquent les techniques.

Depuis **Arène → Mes techniques**, choisir un emplacement (rapide, puissant, ultime ou garde), puis une technique et confirmer le remplacement. L’ancienne reste dans la collection et les techniques de base restent toujours disponibles. Le remplacement est gratuit ; une technique ne peut occuper que son type d’emplacement. Aucun remplacement pendant un combat actif, même replié. Le serveur vérifie possession, type, version de l’équipement et état du duel.

Les techniques récupérées adaptent l’art du champion au combattant : elles ne donnent ni sa classe ni ses statistiques de PNJ. Leurs puissances évoluent proportionnellement à la technique de base du même emplacement au niveau du joueur ; les effets restent fixes. Les ultimes gardent deux actions de recharge. Les avantages sont situationnels et les compromis sont affichés : aucune technique n’est une amélioration automatique dans tous les duels.

## Collection (puissances au niveau 1)

| Champion | Technique | Emplacement | Effet et compromis |
| --- | --- | --- | --- |
| I · Rokhan | Lacération | Puissant | 24 puissance, 78 % précision ; saignement 4 si l’impact touche. Moins de dégâts immédiats que certaines attaques lourdes. |
| II · Brom | Forteresse | Garde | Réduction 55 % ; votre prochaine attaque perd 10 % de puissance. |
| III · Lyss | Croc éclair | Rapide | 11 puissance ; 10 points d’esquive temporaire après impact, plafond total 15 %. Faibles dégâts ; inutile contre les attaques rapides, qui ne peuvent être esquivées. |
| IV · Kael | Griffes enchaînées | Rapide | 11 puissance ; prochaine attaque +20 %, sans cumul. Prépare un assaut au prix de dégâts immédiats faibles. |
| V · Doran | Riposte du rempart | Garde | Réduction 35 % ; après un impact bloqué, prochaine attaque +15 %. Garde inférieure à la normale et aucun bonus sans impact. |
| VI · Nyra | Chasse Fantôme | Ultime | 28 puissance, 94 % précision ; ignore la moitié de la réduction de garde. Moins puissante contre une cible sans garde. |
| VII · Tharos | Exécution rouge | Ultime | 28 puissance, 85 % précision ; +40 % de puissance si la cible a au plus 35 % PV. Peu efficace au début du combat. |
| VIII · Ormund | Fracas du Bastion | Puissant | 22 puissance, 80 % précision ; après impact, la prochaine attaque adverse perd 10 % de puissance. Sacrifie des dégâts immédiats. |
| IX · Selka | Pas de l’Ombre | Garde | Réduction 25 % et 10 points d’esquive temporaire, plafond total 15 %. Fragile contre les attaques rapides. |
| X · Asterion | Défi du Roi | Ultime | 30 puissance, 88 % précision ; +30 % de puissance si vos PV sont au plus à la moitié. Saignement personnel de 3 au prochain tour, même en cas de raté. |

Les pourcentages de précision des attaques puissantes/ultimes précèdent l’esquive adverse. La garde et les bonus de prochaine attaque sont consommés selon les règles du moteur existant. Les effets de techniques sont présents dans les états et le journal du combat.

## Installation

Extraire le correctif à la racine du dépôt et remplacer les fichiers ; ou utiliser le contenu du dossier `Altherya_V0_8_10` du projet complet. Envoyer sur GitHub puis redéployer dans Coolify. Garder le volume de données et la même valeur `ACTIVITY_DB` dans `/app/data`. Aucune variable nouvelle. Le reset concerne uniquement la progression des champions et les techniques, jamais la base entière. Voir INSTALLATION_RESET_CHAMPIONS.md.

Les tables de collection et d’équipement sont créées automatiquement. La sauvegarde est liée à l’identité du joueur existante. L’équipement du début de combat est conservé dans la partie, et le déblocage fait partie de la même transaction que la victoire et son règlement. Une erreur d’écriture annule l’ensemble ; une requête rejouée ne peut pas multiplier les gains ou les techniques.

Bonus du tutoriel : 100 Gold +25 XP, inchangé. Outils et sac : 400 Gold, inchangés. Les récompenses de campagne, quotidiennes, règles de mise, XP, classement et délais de l’arène restent celles de la version précédente. Cette Activity conserve son économie SQLite locale ; cette mise à jour ne branche pas une économie Oddium distante.
