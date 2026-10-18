# Vérification de la réduction Gold

Tests API : suite complète validée (voir nombre dans le résultat ci-dessous).
Tests interface : 67 réussis. Compilation TypeScript et Vite réussie.
Compilation Python réussie.

Les tests couvrent le versement de 10 Gold en campagne, le versement de 30 Gold et 75 XP pour le lot quotidien, les doubles demandes concurrentes, la reprise après redémarrage et les reçus historiques à 115 Gold préservés. La campagne complète de 32 quêtes est également simulée.

Comparaison des catalogues : seuls les 32 champs Gold changent. XP, délais, niveaux, objectifs et dialogues identiques. Bonus de connexion indépendant inchangé. Aucun asset ni placement de menu modifié.

Aucun déploiement distant effectué. Aucun nouveau test visuel navigateur nécessaire pour ce changement de données ; les menus continuent de lire les récompenses du serveur.

Résultat API :

Ran 173 tests in 75.138s

OK
