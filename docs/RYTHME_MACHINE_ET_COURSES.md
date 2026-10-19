# Rythme des machines à sous et des courses

## Machine à sous

Les rouleaux s’arrêtent de gauche à droite. Après le lancement, le premier symbole est révélé vers 4 secondes, le suivant 1,6 seconde plus tard, puis le troisième encore 1,6 seconde après. Un résultat n’est annoncé qu’après les trois arrêts. Le dernier arrêt intervient vers 7 secondes, hors attente réseau supplémentaire. Les commandes restent verrouillées pendant la manche.

Le mode de réduction des animations conserve ce rythme et révèle successivement les symboles, sans déplacement continu des bandes. Il ne transforme plus une manche en résultat instantané.

## Course de chevaux

Décompte de trois secondes, puis environ une minute jusqu’à l’arrivée du premier cheval. Les autres franchissent la ligne quelques secondes après, avec l’ordre et les écarts relatifs déterminés par le serveur. Le départ est progressif, la vitesse remonte en fin de parcours ; le galop conserve sa cadence indépendamment de la taille de la piste. Le statut affiche la phase, le cheval en tête, le temps écoulé et les arrivées.

Le mode de réduction des animations garde la même durée et désactive les poses animées du galop. Le résultat final reste masqué jusqu’à la fin de la présentation.

Aucun changement aux probabilités, cotes, mises, récompenses, prix des outils, bonus de tutoriel ou sauvegardes. Le serveur règle la manche comme auparavant ; ces changements portent sur sa présentation. Les fichiers API de production restent identiques. Aucun nouvel asset nécessaire. Les nouveaux assets de roulette livrés précédemment sont conservés.

## Vérification

- Construction TypeScript/Vite et 152 tests interface réussis.
- Compilation syntaxique de 90 modules Python ; 3 tests serveur machines à sous et 3 tests courses réussis.
- Navigateur avec API réelle et base temporaire : PC 1440×900 en animation normale et mobile 390×844 en réduction des animations. Mesure réelle de chaque arrêt, ordre gauche/droite et espacement ; vérification des rouleaux centrés, commandes bloquées, résultat et portefeuille.
- Courses laissées jusqu’au terme réel dans les deux modes ; vérification qu’aucun cheval n’est déjà arrivé après les premières secondes, que les chevaux avancent et galopent en mode normal, que le classement et le solde correspondent au serveur.
- Archives vérifiées par CRC ; autres jeux et assets conservés. Pas de test dans le client Discord ni sur les données de production.

## Installation

Copier le contenu du dossier Altherya_V0_8_10 du correctif dans le projet actuel, envoyer sur GitHub puis reconstruire/redéployer dans Coolify. L’archive complète contient aussi les autres jeux et tous les assets précédents. Conserver la base de données et les variables d’environnement. Aucun déploiement distant réalisé.
