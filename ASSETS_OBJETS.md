# Assets des objets d’Altherya

La collection complète comporte 151 illustrations sur dix planches PNG transparentes :
120 objets d’histoire, 15 compléments d’expédition (deux plantes, neuf ressources
animales distinctes et quatre accessoires), et 16 pièces narratives pour les quêtes.
Les 21 ressources qui avaient déjà une illustration dédiée et les outils existants
conservent leurs images. Les 32 ressources du catalogue ont ainsi un visuel associé.

Les noms canoniques du jeu sont conservés. Les objets abstraits de l’histoire sont
représentés par des emblèmes ou des reliques ; les cartes, documents, bijoux, armes,
caisses et objets de voyage sont illustrés selon leurs noms. Les correspondances
exactes passent avant la tolérance aux accents, apostrophes ou émojis, afin de ne pas
confondre des objets de chapitres différents portant un intitulé proche.

## Où les trouver

- `apps/game/public/assets/items/` : les dix planches originales.
- `apps/game/public/assets/items/catalogue.html` : galerie de tous les objets,
  consultable après déploiement via `/assets/items/catalogue.html`.
- `apps/game/src/ui/item-manifest.json` : correspondances nom, planche, cellule et chapitre.
- `apps/game/src/ui/generated-item-art.ts` : résolution des illustrations par nom.
- `ASSETS_OBJETS_PROMPTS.json` : consignes de génération des planches.

Les planches sont des atlas de quatre colonnes et quatre lignes. Le navigateur
isole une cellule par SVG, avec découpe explicite : les menus ne montrent pas
l’ensemble de la planche. Les pixels et la transparence des images sont conservés.
Les dimensions réelles des PNG sont enregistrées dans le manifeste.

## Intégration

Les objets d’histoire ont leurs images au marché et dans l’inventaire du profil.
Les ressources utilisent leurs images dans le marché, la forge, l’inventaire et
les découvertes d’expédition. Le journal des quêtes affiche une pièce narrative
liée à la quête ou la ressource demandée, lorsqu’il s’agit d’une livraison.
Les quatre accessoires possèdent leurs visuels de préparation, mais restent
indisponibles comme auparavant : aucun bonus ni mécanisme d’équipement n’est ajouté.
Les 16 pièces de quête sont des illustrations narratives, pas de nouveaux objets
accordés au joueur, consommés ou vendus.

## Installation

Remplacer les fichiers du dépôt par ceux de l’archive complète puis redéployer
sur Coolify. Le correctif ne contient que les changements de cette livraison et
s’extrait à la racine du projet actuel, là où se trouve `apps/`. Conserver les
variables et le volume de données. Aucun reset n’est demandé.
Les prix, tables de butin, récompenses, tutoriel, combats, noms et sauvegardes ne
sont pas modifiés. Aucun déploiement distant n’a été effectué.
