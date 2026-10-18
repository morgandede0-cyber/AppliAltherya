# Audit — portail permanent Altherya

## Changements

- Salon 1551927225253761044, application 1529936499775242250.
- Message unique du bot, bouton Discord natif « Jouer à Altherya », vue persistante, épinglage si autorisé.
- Enregistrement du message et bail d’un seul worker dans la base Activity ; reprise après redémarrage, détection du message manquant, récupération d’un portail épinglé/récent après interruption.
- Réponse native LAUNCH_ACTIVITY (12) immédiate ; aucun follow-up public ajouté par le gestionnaire. Point d’entrée global modifié uniquement sur son handler, sans synchroniser ni supprimer les autres commandes. Les lancements hors du salon portail reçoivent une orientation privée.
- Token vérifié contre l’ID d’application ; détection d’un endpoint HTTP d’interactions existant et refus de l’écraser. Worker Gateway intégré au cycle de vie de l’API. Aucun endpoint HTTP non signé ajouté.
- Nouvelle dépendance API fixée et testée : discord.py 2.7.1. Aucun intent privilégié ni entrée en vocal nécessaire.
- Utilitaire explicite de restauration du point d’entrée Discord ; jamais exécuté automatiquement.
- Fichier apps/game/src/data/rules.ts rétabli depuis la copie source locale d’origine, compatible avec ses consommateurs identiques. Il avait été exclu par erreur de l’archive complète précédente. Le nouveau ZIP conserve les répertoires de données **source** et exclut seulement les données runtime/caches et secrets.

## Vérifications locales

- Compilation de tous les modules Python API et moteurs du bot : réussie.
- Suite API complète : **120 tests réussis**, dont 26 tests spécifiques du portail ; puis ajout et réussite des **4 tests de l’utilitaire de restauration** (30 tests ciblés portail/restauration réussis). Total : **124 tests API distincts vérifiés**.
- Tests portail : création unique, deux ready concurrents, ID conservé, récupération d’un message épinglé/récent, 403 sans doublon, suppression/recréation, refus de modifier un message étranger, épinglage refusé sans republication, bon token/app, endpoint HTTP non écrasé, point d’entrée conservant les autres commandes, création si absent, launch sans follow-up, clic rapide, mauvais salon, erreur/réessai, commande inconnue ignorée, bail concurrent, arrêt sans token/flag désactivé.
- La vraie méthode discord.py InteractionResponse.launch_activity est exécutée avec transport HTTP simulé : payload réellement généré **{"type":12}** ; pas seulement un mock de la méthode de lancement.
- TypeScript/Vite et **47 tests frontend** : réussis après restauration du fichier manquant.
- Chromium : **38 contrôles admin** et **24 contrôles tutoriel**, sans erreur JS. PC 1440×900, fenêtre courte 1186×570, mobile 390×844.
- Comparaison à la version Logs Discord actuelle : aucun asset, menu, règle serveur économique ou liste d’admins modifié. Source frontend uniquement restaurée, sans ajout de nouveaux équilibres au gameplay Activity.
- Archives : CRC vérifié ; fichier règles requis vérifié dans le ZIP complet ET le correctif. Reconstruction TypeScript/Vite effectuée à partir de l’archive complète extraite, avec dépendances locales de test, pour confirmer la complétude du livrable.

## Limites et vérification serveur requise

Aucun accès authentifié à votre Coolify ou au bot réel : aucun portail, message, épingle ou commande globale n’a été publié/modifié depuis cet environnement. Les appels Discord des tests sont simulés. La mise à jour du point d’entrée est préparée dans le code et se produit lors du déploiement ; vérifier les permissions et le bon token, puis tester dans Discord avec deux joueurs.

Le portail ne peut pas empêcher l’affichage d’une interface par joueur ni contrôler toutes les cartes natives de Discord. Il n’ajoute pas de messages publics par clic et réutilise son propre message. Les ouvertures depuis d’autres applications/clients et les sessions Discord existantes restent gérées par Discord. Il ne crée pas un monde multijoueur synchronisé supplémentaire.

La déduplication normale est persistante ; une panne entre envoi et sauvegarde suivie d’une longue interruption, d’un portail non épinglé et de plus de 100 messages récents peut encore empêcher la récupération. Une seule base partagée par ce service est prise en charge ; plusieurs déploiements avec des bases indépendantes ne se coordonnent pas.

L’économie reste la SQLite isolée de l’Activity. Le partage Gold Oddium/PostgreSQL n’est ni modifié ni validé en production par cette mise à jour. Aucun reset, suppression de données ou changement de port. Le tutoriel illustré, les récompenses uniques et les logs/Gazette précédents sont conservés.

## Documentation primaire utilisée

- https://docs.discord.com/developers/interactions/receiving-and-responding
- https://docs.discord.com/developers/activities/development-guides/user-actions
- https://docs.discord.com/developers/activities/development-guides/multiplayer-experience
- https://discordpy.readthedocs.io/en/stable/interactions/api.html
