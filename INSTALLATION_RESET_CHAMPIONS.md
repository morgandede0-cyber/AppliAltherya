# Reset unique des champions et techniques

Cette version remplace le déblocage rétroactif des techniques. Au premier démarrage après déploiement :

- tous les joueurs repartent au champion I (compteur de champions vaincus à zéro) ;
- toutes les techniques dérobées et tous les choix d’équipement sont effacés ; les quatre techniques de base, adaptées au niveau, restent disponibles ;
- le délai des champions est levé pour permettre de recommencer immédiatement ;
- Gold, Banque, XP, niveau, classement d’arène, historique des combats, statistiques, tutoriel, inventaire, histoire et quotidiennes sont conservés.

Ensuite, chaque technique se gagne uniquement par une nouvelle victoire contre son champion. Le compteur de victoires seul n’accorde plus de techniques automatiquement. Un marqueur durable empêche le reset de se répéter lors des redémarrages suivants. Les nouvelles victoires et techniques équipées restent enregistrées.

## Installation

Remplacer les fichiers du dépôt par le correctif ou le contenu du dossier racine du projet complet, envoyer sur GitHub puis redéployer dans Coolify. Conserver le volume et la même base `ACTIVITY_DB` : ne jamais supprimer la base pour appliquer ce reset. Aucune variable supplémentaire ni commande SQL manuelle n’est nécessaire.

Au démarrage, les parties interrompues suivent le mécanisme existant de remboursement unique des mises. Une copie complète et vérifiée de la base est créée avant le reset. Le reset et son marqueur sont enregistrés dans une seule transaction : en cas d’échec, aucune remise à zéro partielle n’est conservée et le démarrage suivant peut réessayer.

Contrôler Arène → Champion I, puis Mes techniques : seules les techniques de base doivent être équipées. Gagner contre Rokhan débloque uniquement Lacération. Après redémarrage, cette victoire et le choix d’équipement doivent rester présents.

## Validation

26 tests ciblés de l’arène réussis, dont quatre pour le reset. Neuf contrôles navigateur réussis sur PC et mobile, sans erreur JavaScript.

Tests dédiés : tous les joueurs remis au champion I, autres données conservées, collection vide, absence de rattrapage même avec un compteur élevé, nouvelle victoire donnant une seule technique, équipement et progression conservés au redémarrage, remboursement unique d’une mise interrompue, rollback d’un reset échoué et nouvel essai possible. Compilation Python et tests de régression de l’arène inclus.

Parcours navigateur sur PC et mobile : migration d’une base simulant dix anciens champions vaincus, collection verrouillée, victoire contre le premier champion, acquisition et équipement de Lacération, puis redémarrage sans nouveau reset. Les tests utilisent des données temporaires ; aucune base de joueurs n’est incluse dans les fichiers livrés.

Le reset se produira sur le serveur lors du redéploiement. La livraison des fichiers ne modifie pas à elle seule le serveur distant. Le bonus du tutoriel reste 100 Gold +25 XP et les outils/sac restent à 400 Gold.
