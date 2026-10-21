# Pierre · Feuille · Ciseaux

Le jeu est accessible par Taverne → Les jeux → Pierre feuille ciseaux.

Le modèle de table face au tavernier est conservé : tapis rouge continu, trois plaques en bois pour choisir son geste, mise au centre, bouton Jouer et règles. Les mains sont des sprites transparents distincts du fond : trois poses pour le joueur, trois poses pour le renard. Trois mouvements synchronisés précèdent une révélation simultanée, avec des ombres et des sons de contact optionnels.

## Règles conservées

- Pierre bat Ciseaux ; Ciseaux bat Feuille ; Feuille bat Pierre.
- Mise entière de 1 à 500 Gold, limitée au portefeuille.
- Victoire : retour total de deux mises ; égalité : mise rendue ; défaite : mise perdue.
- Le serveur choisit le geste adverse, débite et règle la manche une seule fois. La révision protège contre le rejeu d’une demande.
- La présentation animée ne modifie ni les probabilités, ni les récompenses, ni le Gold existant.

Les deux mains restent fermées pendant les trois mouvements. Les boutons, les touches de retour et la saisie de mise sont verrouillés jusqu’à la fin. Le bouton Son permet d’activer les sons synthétiques ; ils sont muets par défaut. La préférence système de réduction des animations montre directement le résultat. Les règles disposent d’un focus clavier et d’une fermeture par Échap.

## Installation

Remplacer dans le projet les fichiers contenus dans le dossier Altherya_V0_8_10 du correctif. Ne pas effacer la base de données ou les variables d’environnement. Envoyer les modifications sur GitHub, puis reconstruire/redéployer via Coolify. L’archive complète contient aussi toutes les modifications précédentes. Cette livraison ne déploie pas le serveur et ne touche pas à la base de production.

## Fichiers principaux

`apps/game/src/ui/tavern-rps.ts`, `tavern-rps.css`, `rps-model.ts` et branche de routage dans `live-games.ts`.

Assets dans `apps/game/public/assets/rps/` : `table.png`, `player.png`, `fox-v2.png`. Les atlas comportent trois cellules horizontales, dans l’ordre Pierre / Feuille / Ciseaux. L’atlas de boutons existant `assets/blackjack/controls-atlas.png` est inclus comme dépendance du correctif. Les montants, le résultat et la sélection sont des éléments natifs interactifs.
