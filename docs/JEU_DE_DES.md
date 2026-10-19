# Jeu de dés de la taverne

Le décor approuvé est intégré à une table dédiée. Les données, mises, boutons et résultats sont des éléments interactifs. Deux assets sont ajoutés : le décor nettoyé et la texture ivoire des dés. Le tavernier et le décor restent fixes.

## Dés en volume

Les dés utilisent une géométrie WebGL à arêtes arrondies, des normales lissées, la texture ivoire, un éclairage chaud et des reflets qui évoluent avec les rotations. Les points sont calculés précisément et présentent un effet de creux. Les faces opposées totalisent sept. Chaque résultat est placé sur la face supérieure avant l’orientation de la caméra.

Les trajectoires comprennent un déplacement, plusieurs rebonds d’amplitude décroissante et un ralentissement des rotations. Le premier dé s’arrête avant le second. Les ombres suivent les dés. Les mouvements sont pilotés pour présenter les deux valeurs du serveur ; ce n’est pas un moteur de simulation physique ou de collisions entre objets.

Si WebGL est indisponible ou son contexte perdu, les six faces en CSS 3D prennent le relais. La réduction des animations affiche rapidement les positions finales. Les ressources graphiques sont réutilisées à chaque changement de mise et libérées à la fermeture de la table.

## Sons et contrôles

Le bouton « Son : OFF / ON » permet d’activer ou couper l’audio. Les contacts utilisent de courts sons synthétiques, atténués au fil des rebonds, puis le signal de résultat existant. Aucun son ne se lance lorsque l’audio est coupé. Le réglage utilise le mécanisme audio déjà présent dans le jeu.

La mise reste comprise entre 1 et 500 Gold, sous réserve du portefeuille disponible. Victoire : retour total de deux fois la mise ; égalité : mise restituée ; défaite : mise perdue. Le serveur décide des deux valeurs et du règlement. Les commandes et Échap sont verrouillés pendant la présentation du lancer. Les informations de résultat apparaissent après l’arrêt des deux dés.

Les bonus du tutoriel, le prix des outils et les règles économiques ne changent pas. Les autres jeux et menus sont conservés.

## Installation

Copier la mise à jour dans le projet, envoyer sur GitHub puis redéployer dans Coolify avec la construction habituelle du client. Le ZIP complet contient les intégrations précédentes, dont les courses et la roulette russe. Pas de migration destructive ni d’effacement de joueurs.

## Vérifications locales

- `npm --prefix apps/game run build`
- `npm --prefix apps/game test`
- `PYTHONPATH=apps/api:apps/api/tests python3 -m unittest test_play test_dice_presentation -v`
- `node apps/game/tests/browser-dice.cjs` avec Chromium Playwright installé.

Variables facultatives du parcours navigateur : CHROMIUM_EXECUTABLE, CHROMIUM_ARGS, DICE_PORT, DICE_VIEWPORTS ; DICE_FORCE_FALLBACK active le scénario de test sans WebGL. Les parcours créent une base temporaire et ne touchent pas aux données de production.
