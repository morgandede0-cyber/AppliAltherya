# Smogo dans la ruelle — 24 octobre 2026

La ruelle dispose de deux images complètes : une version avec Smogo, une version sans lui. La seconde proposition remplace la première illustration refusée : le personnage est plus discret, les couleurs violettes sont atténuées et la fumée se concentre au sol. Aucune image de personnage séparée n’est superposée dans le jeu.

Le décor suit les passages transmis par le serveur. À la fin d’une visite, l’accès au personnage se désactive immédiatement, puis le décor sans Smogo prend sa place dès son chargement. Le client tient compte de l’heure serveur et du temps écoulé ; il ne dépend pas de l’heure civile de l’appareil. Les nouvelles visites sont reçues lors des actualisations existantes du jeu (15 secondes au maximum hors interruption réseau). Les images sont décodées avant affichage ; une ancienne requête de chargement ne peut pas réafficher Smogo après un départ ou un changement de scène.

Le bouton Smogo est positionné sur le personnage. Le voleur, le braqueur, le vigile et le panneau de retour restent accessibles. Le second retour générique qui recouvrait les commandes du bas est retiré uniquement de la ruelle. Après le départ de Smogo, une énigme payée et non expirée peut être reprise avec « Reprendre l’énigme ». Aucun nouveau pari ne peut être engagé en son absence ; les contrôles serveur existants sont conservés.

## Vérification

- Compilation TypeScript et build de production réussis (avertissement Vite de taille des fichiers déjà présent).
- 228 tests d’interface et 24 tests serveur de Smogo passent.
- Cinq tests ciblés vérifient l’arrivée, le départ, l’échéance serveur, la reprise d’une mise engagée, les chargements tardifs, la destruction de la scène et la reprise après erreur de chargement.
- 30 contrôles navigateur réussis, sans erreur JavaScript, avec le jeu et l’API réels, base temporaire : PC 1440×900, mobile 390×844 et 320×568. Présence/absence, clics, géométrie des quatre panneaux, reprise du même tour et absence de second prélèvement sont vérifiés.
- Journal des mises à jour : ouverture, pagination et détails couverts par les tests d’interface.

Aucun code de backend en production, prix, récompense, horaire de visite ni sauvegarde de joueur n’a été modifié. Les tests de Gold utilisent une base locale temporaire ; la base partagée Oddium en production et les sessions Discord réelles n’ont pas été utilisées. Aucun déploiement automatique.

## Assets et réalisation

Assets : apps/game/public/assets/scenes/alley-smogo-present-v2.png et alley-smogo-absent-v2.png. Génération intégrée d’images, à partir du décor original et de l’identité existante de Smogo. Les panneaux transparents existants restent des boutons indépendants.

Consigne artistique de la scène présente : recomposer une illustration cohérente de la ruelle médiévale, conserver ses trois PNJ, intégrer un félin encapuchonné violet sombre dans le passage, plus en retrait, avec proportions, ombres de contact, éclairage ambre et fumée volumétrique discrète cohérents. Pas d’interface dessinée dans l’image.
Consigne de la variante absente : retirer uniquement Smogo et sa fumée de cette scène ; restaurer le passage et conserver le cadrage, la lumière, les trois PNJ, les objets et l’architecture.
