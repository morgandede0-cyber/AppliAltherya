# Correctif Brave V0.1.1

La capture montrait une interface chargée avec une scène vide. L’erreur content.js ne permettait pas de déterminer la cause du rendu : aucun diagnostic certain de WebGL n’est affirmé.

## Adaptation

Cette version utilise un moteur de rendu de compatibilité Canvas 2D pour tous les navigateurs, dont Brave. Le client ne demande plus de contexte WebGL/WebGPU. Les PNG du décor et des personnages, le recadrage des frames, les animations, la caméra, les collisions et le gameplay sont conservés. PixiJS reste une dépendance du projet précédent, mais n’est plus importé par le client de cette version. Ce choix réduit la dépendance à l’accélération graphique pour cette première scène ; les performances devront être mesurées avant d’agrandir le monde.

Les erreurs de chargement ou d’exécution sont affichées dans le jeu. Chargement d’image limité à 15 secondes. Un script DEMARRER_BRAVE.bat facilite le lancement sur Windows. Il ouvre le navigateur par défaut ; sélectionner Brave comme navigateur par défaut ou ouvrir manuellement http://localhost:8080.

## Tests

11 tests Node réussis : les 9 tests de gameplay/sauvegarde existants et 2 tests du rendu Canvas (transformations caméra, position/échelle, recadrage du sprite, ancrage, visibilité et retournement). TypeScript strict et construction Vite réussis. Les 4 tests Python gateway et compilation Python passent. Ces tests de rendu utilisent un contexte instrumenté : ils ne constituent pas un essai visuel dans Brave.

Aucun Brave local n’est accessible ici. L’affichage réel sur le PC de l’utilisateur reste à confirmer. La cause initiale n’est pas prouvée ; cette livraison apporte un chemin de rendu indépendant de WebGL et des erreurs visibles pour poursuivre le diagnostic.

## Installation

Arrêter l’ancien serveur avec Ctrl+C, extraire ce nouveau ZIP dans un nouveau dossier, puis lancer DEMARRER_BRAVE.bat. Garder la fenêtre serveur ouverte. Ouvrir http://localhost:8080 dans Brave et faire Ctrl+F5 pour renouveler les fichiers JS/CSS. La clé de sauvegarde locale est conservée et aucune suppression de progression n’est effectuée.
