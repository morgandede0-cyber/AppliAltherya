# Menus interactifs transparents

Les menus utilisent les titres, boutons, illustrations et matériaux des assets existants. Le fond extérieur est transparent pour laisser apparaître les scènes. Les panneaux de bois et de parchemin encadrent les données réelles et les contrôles interactifs.

## Couverture
Banque, forge, marché (achat, vente et objets d’histoire par chapitre), taverne, tavernier, troubadour, jeux, château, tableau de bord, podium, arène, techniques, ruelle, voleur, braqueur, vigile, salle clandestine, métiers, outils, expéditions, profil, journal, monde et dialogues.

Les boutons et les panneaux se réorganisent sur mobile. Le marché conserve quatre objets par page et la séparation des objets d’histoire. Les jeux conservent leurs animations, contrôles et résultats du serveur. La Garde affiche son effet défensif plutôt qu’une puissance absente. La banque conserve sa présentation validée, sans fond gris ni coffre central.

## Validation locale
- Compilation TypeScript/Vite réussie.
- 43 tests frontend et 36 tests API réussis : 79 au total.
- 186 contrôles navigateur dans six suites : assets/menus 99, jeux 20, placement 16, couches 38, braquage 10, banque 3.
- Vérifications des proportions et centrages des images, débordements, fonds transparents, interactions et présentation PC/mobile ; contrôle visuel de plusieurs parcours.

Le code API et bot est identique à la version précédente. Cette livraison adapte la présentation ; elle ne réintroduit pas la mise à jour annulée des contrats et ressources. Les fonctions déjà incomplètes de Khaz/Ashkar restent dans leur état antérieur. Aucun déploiement ni contrôle de la base de production, de Discord ou du serveur Coolify n’a été effectué : la persistance partagée doit être vérifiée sur votre serveur.
