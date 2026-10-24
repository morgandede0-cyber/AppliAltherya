# Remise à zéro globale du tutoriel

La nouvelle révision `wolf-twelve-required-20261024-v1` remplace `illustrated-20261015-v1`.

Au redéploiement :
- La liste admin des tutoriels terminés exclut les validations de l’ancienne révision et repart à zéro.
- Chaque joueur recommence à l’étape 1 à sa prochaine connexion ; anciennes visites et mode relecture sont remis à zéro sous transaction.
- Le jeu reste verrouillé jusqu’à la fin du nouveau guide.
- Les reçus et drapeaux de récompense ne sont pas effacés. Un ancien joueur ne reçoit pas un second paiement.
- Un nouveau joueur n’ayant jamais touché la récompense reçoit normalement 100 Gold et 25 XP.
- Le nouveau parcours conserve ensuite sa progression aux reconnexions et aux redémarrages.

L’opération n’efface aucun inventaire, niveau, quête ou solde. Aucun SQL manuel ni effacement de base requis. Après copie de la mise à jour cumulative sur le projet existant, reconstruire et redéployer dans Coolify, avec redémarrage de l’API.

Tests : 33 tests serveur du tutoriel et 249 tests client, construction TypeScript/Vite et compilation Python. Deux tests couvrent explicitement la révision utilisée en production auparavant. Les comptes et la base des tests sont temporaires ; le déploiement de production reste à effectuer.
