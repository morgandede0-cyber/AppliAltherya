# Roulette russe : table et compteurs animés

Le modèle approuvé à barillet fermé est intégré à une table dédiée. Le décor nettoyé, le revolver transparent et la cartouche sont des assets séparés. Les textes, mises, compteurs, états des chambres et boutons restent de vrais éléments interactifs. Le revolver conserve sa position sur le tapis ; les mouvements discrets accompagnent le chargement, les passages et la fin de manche. Il s’agit d’une animation 2D, pas d’une simulation mécanique en 3D.

## Compteurs et déroulement

Les règles existantes restent identiques : une seule balle dans six chambres, un passage du joueur suivi de celui de la hyène. Le bouton Tenter sa chance peut donc résoudre une ou deux chambres. Le serveur transmet uniquement les événements déjà résolus, sans révéler la position future de la balle.

Chaque passage est présenté séparément : acteur annoncé, indicateur animé, chambre vide ou balle tirée, décompte des chambres restantes. La cartouche reste affichée à 1 tant qu’elle est chargée, puis passe à 0 avec une disparition animée lorsqu’elle est tirée. Elle indique aussi 0 en cas de remboursement de la manche. Les chambres non jouées restent inconnues.

Le bouton « Encaisser » de la maquette a été remplacé par « Règles » : le moteur existant ne propose pas d’encaissement anticipé. Une victoire retourne deux fois la mise totale ; une défaite perd la mise. La mise doit être un entier positif dans les limites du casino. Les bonus du tutoriel, les prix des outils et l’économie ne sont pas modifiés.

Les commandes sont verrouillées pendant les animations. Quitter la table entre deux actions conserve la manche et sa mise ; revenir affiche le bon nombre de chambres. Le mode de réduction des animations abrège les transitions. Au redémarrage du serveur, le remboursement des manches interrompues conserve le comportement existant.

## Installation

Copier les fichiers de la mise à jour dans le projet, mettre à jour GitHub puis redéployer dans Coolify. Le ZIP complet inclut aussi les précédentes intégrations du blackjack, de la roulette, des machines à sous et des courses de chevaux. Aucun effacement de données ni changement de configuration de production n’est nécessaire.

## Vérification

- `npm --prefix apps/game run build`
- `npm --prefix apps/game test`
- `python3 -m unittest discover -s apps/api/tests`
- `node apps/game/tests/browser-russian.cjs` avec Chromium Playwright installé (variables facultatives CHROMIUM_EXECUTABLE, CHROMIUM_ARGS, RUSSIAN_PORT et RUSSIAN_VIEWPORTS).

Les essais navigateur utilisent une base temporaire et ne modifient pas les comptes de production.
