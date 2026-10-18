# Audit — relais Discord Activity

## Livré

Trois salons par défaut configurés ; outbox SQLite persistante, worker aiohttp intégré au cycle de vie de l’API, logs sur modifications réelles côté serveur, accueil après tutoriel, niveaux, victoires et gains au Hall de Gloire, Gazette quotidienne à 9 h Europe/Paris. Fin des expéditions hors connexion. Actions administrateur et notification atomiques. Toutes les références d’identité viennent des profils OAuth stockés, pas du navigateur.

## Vérifications effectuées localement

- Compilation de tous les modules Python API et bot : réussie. Lecture des imports des modules modifiés ; aucune nouvelle dépendance hors aiohttp déjà présent et bibliothèque standard.
- Suite API : **94 tests réussis**, dont **18 tests du relais** (routes exactes, absence de spam au polling, actions refusées, conservation après redémarrage, répétition légitime d’un dépôt, résultat net d’un jeu, Gazette quotidienne/date, nom sans mention, transaction admin annulée, invité ignoré, XP total lors d’un niveau, expédition terminée hors connexion, accusé d’envoi, nonce stable au réessai, 429, 401, 403 et claim concurrent).
- TypeScript et build Vite : réussis. **47 tests frontend réussis**.
- Navigateur Chromium : **38 contrôles admin** et **24 contrôles tutoriel**, sans erreur JS. PC 1440×900, fenêtre courte 1186×570 et mobile 390×844.
- Comparaison byte à byte avec la version Tutoriel illustré précédente : aucun menu, asset ou moteur original du bot modifié. Seuls activity.py, activity_admin.py et server.py sont raccordés au nouveau discord_events.py ; test et documentation ajoutés.
- Archives ZIP : vérification CRC et liste des entrées, exclusions des dépendances, caches, bases utilisateur et secrets. Le build est refait par Docker au déploiement.

## Points restant à vérifier sur le serveur

Aucun accès à Coolify ni token du bot disponible ici. Aucun message envoyé dans les salons réels. Il reste à ajouter DISCORD_BOT_TOKEN (runtime uniquement), vérifier les permissions du bot, redéployer et effectuer une action depuis l’Activity. Les tests HTTP Discord utilisent des réponses simulées, pas le réseau réel. Les tests navigateur utilisent des profils OAuth de fixture, pas votre compte.

La base reste celle de l’Activity : SQLite isolée. Aucun test de Gold partagé avec Oddium/PostgreSQL en production n’a été réalisé ; ce relais ne change pas cette architecture. Les anciennes données ne sont pas importées et la Gazette d’un ancien bot séparé doit être désactivée si elle est encore publiée dans le même salon.

La file prévient les doublons d’événements observés et confirme les envois ; la fenêtre de nonce Discord est limitée à quelques minutes. Un arrêt après envoi accepté mais avant accusé local peut encore causer un doublon après une longue interruption. Les notifications gameplay sont des observations après commit, pas un journal comptable atomique de tous les moteurs : une interruption peut faire perdre le détail d’une action intermédiaire. Ces limites sont décrites dans INSTALLATION_LOGS_DISCORD.md.

Aucun changement de menus, d’équilibrage, de port, de whitelist admin ni nouvelle remise à zéro du tutoriel.
