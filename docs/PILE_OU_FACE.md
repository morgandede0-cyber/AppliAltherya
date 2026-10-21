# Pile ou face animé

Ouvrir Taverne → Les jeux → Pile ou face. Choisir le blason (Pile) ou le lion couronné (Face), puis miser entre 1 et 500 Gold dans la limite du portefeuille. Victoire : retour total de deux mises ; défaite : mise perdue. Les règles et les gains existants sont conservés.

La pièce comporte deux faces transparentes et une tranche composée de 64 segments en CSS 3D. Elle monte, tourne, retombe et effectue trois contacts amortis avec le tapis. L’ombre suit la hauteur ; les faces s’assombrissent selon l’inclinaison. Le résultat final provient du serveur et correspond à la face visible. La trajectoire est une présentation animée de ce résultat, sans moteur physique de collisions.

Les boutons et la mise restent verrouillés pendant la demande et le lancer. Échap ne permet pas d’interrompre une manche réglée. Le serveur conserve sa protection par révision contre une même demande rejouée. Les règles s’ouvrent dans une fenêtre avec focus clavier. Les sons synthétiques sont désactivés par défaut et activables dans le jeu. La préférence système de réduction des animations affiche directement le résultat.

## Installation

Décompresser la mise à jour et remplacer les fichiers correspondants dans le projet existant (le dossier Altherya_V0_8_10 contient la racine du projet). Ne pas supprimer la base de données ou les variables d’environnement. Envoyer les fichiers sur GitHub puis reconstruire/redéployer via Coolify. Le ZIP complet contient également toutes les modifications précédentes. Aucun déploiement de production n’est effectué par cette livraison.

## Assets

`apps/game/public/assets/coin/` : `pile.png`, `face.png`, `edge.png`, `table.png`.
Les zones de texte et boutons sont natives et interactives ; les montants ne sont pas inscrits dans le fond.
