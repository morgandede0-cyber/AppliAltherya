# Courses de chevaux

La salle clandestine ouvre désormais une table de course dédiée : piste miniature, quatre portraits sélectionnables, mise libre, jetons et lancement. Les éléments interactifs utilisent le décor approuvé et les boutons du casino. Sur mobile, la piste complète reste visible et les choix passent sur deux colonnes.

## Animation

Les quatre chevaux possèdent des planches transparentes avec quatre angles de vue et des phases de galop (8 phases pour Éclair, Cendre et Furie ; 7 pour Minuit). Les rectangles et contours de chaque pose sont mesurés séparément : les images ne sont pas découpées arbitrairement en cases égales. Les silhouettes excluent les petits fragments des poses voisines.

Le moteur Canvas suit quatre trajectoires ovales en perspective. La cadence dépend de la distance parcourue, avec accélération au départ, variation de progression, changement de vue dans les virages, ombres et poussière discrète. Le décor intérieur masque les portions éloignées pour respecter la profondeur. Il s’agit d’une animation 2D par poses, pas d’une simulation physique 3D.

Un décompte précède le départ. Les commandes sont verrouillées pendant la course, puis le classement complet et le retour/net du pari apparaissent. Le mode de réduction des animations présente rapidement le résultat. La fermeture détruit les écouteurs et arrête le rendu.

## Résultat et mise

Le serveur conserve les probabilités et règles de paiement existantes. Il transmet désormais le classement complet et les temps d’arrivée associés au vainqueur. Le client affiche ce résultat ; il ne décide pas du gain. Une cote devenue périmée est refusée avant le prélèvement. Les révisions empêchent de régler deux fois une même demande.

Les cotes des quatre portraits après la course sont celles du prochain pari. La dernière course conserve ses propres cotes dans son résultat serveur. La mise maximale, l’accès par le vigile, les récompenses du tutoriel et les prix des outils ne changent pas.

## Installation

Copier le contenu de la mise à jour dans le projet existant, mettre à jour GitHub puis redéployer dans Coolify avec la construction habituelle du client et le redémarrage du serveur. Aucune migration destructive ni réinitialisation des joueurs n’est nécessaire. Le ZIP complet contient aussi les changements précédents du blackjack, de la roulette et des machines à sous.

## Validation locale

- `npm --prefix apps/game run build`
- `npm --prefix apps/game test`
- `python3 -m unittest discover -s apps/api/tests`
- `node apps/game/tests/browser-horses.cjs` (Chromium Playwright installé ; les variables facultatives CHROMIUM_EXECUTABLE et CHROMIUM_ARGS permettent un navigateur fourni par l’environnement).

Les parcours navigateur créent une base temporaire et testent l’accès réel, la mise, le verrouillage, le galop, les résultats, le solde, les règles et le retour à la salle. Aucune base de production n’est utilisée.
