# Audit de sécurité Altherya — 21 octobre 2026

## Résultat et périmètre

Audit du projet complet nettoyé (version 6 de l’archive source), avec corrections intégrées. Aucun contournement de l’accès admin ni création illicite de Gold n’a été reproduit dans les scénarios exécutés. Cette conclusion est limitée aux chemins inspectés et aux tests décrits ici ; elle ne garantit pas l’absence de toute faille.

L’analyse porte sur l’API Activity, les sessions et l’identité Discord, les transactions, les moteurs de jeu, les principaux garde-fous du bot et les dépendances. Toutes les manipulations utilisent des bases temporaires. Le serveur altherya.magicgg.fr, la configuration réelle Coolify/Nginx et les salons Discord n’ont pas été attaqués ou modifiés.

## Problèmes corrigés

| Point | Risque constaté | Correction |
| --- | --- | --- |
| Sessions sans échéance côté serveur | Moyen : une personne possédant déjà un cookie volé pouvait le réutiliser sans limite temporelle. Ce n’est pas une preuve de vol de cookie. | Échéance absolue de 30 jours, vérifiée sur les accès et la liaison OAuth. Rotation du token et de son échéance dans la même transaction. Cookie aligné sur cette durée. |
| Appels anonymes coûteux sans quota | Moyen, disponibilité : création répétée de sessions et profils, lecture de snapshots et appels OAuth possibles sans frein applicatif. | Admission limitée avant traitement coûteux. Les cookies arbitraires et X-Forwarded-For ne sélectionnent pas les quotas. Mémoire du limiteur bornée à 4 096 entrées. |
| POST invalide ou sans session créant des données | Faible à moyen : l’allocation pouvait précéder le rejet de l’action. | Validation de la forme de la demande avant allocation ; POST sans session valide refusé en 401, demande mal formée en 400. |
| JSON OAuth non objet | Faible : un tableau JSON pouvait déclencher une erreur serveur au lieu d’un rejet contrôlé. | Réponse 400 avant tout appel OAuth externe. |
| Ancienne dépendance multidict autorisée | Moyen selon l’avis officiel : la version 6.7.1 du runtime de test est affectée par une fuite mémoire conditionnelle. L’exploitation dans Altherya n’a pas été démontrée. | Ajout de la contrainte multidict>=6.9.1,<7, installation et vérification de la version corrigée 6.9.1. |

La migration crée une table d’échéance distincte, sans modifier les comptes, soldes ou récompenses existants. Les sessions existantes reçoivent une échéance au premier démarrage de cette mise à jour ; les redémarrages suivants ne la repoussent pas. Après expiration, la reconnexion Discord retrouve le même compte. La rotation ne déconnecte pas les autres appareils.

Protection complémentaire : rejet des POST déclarés cross-site par le navigateur en plus de l’en-tête applicatif existant, et en-tête X-Content-Type-Options: nosniff sur les réponses API traitées. Les réponses privées conservent les règles de cache adaptées ; les avatars restent en cache privé.

## Quotas et limites opérationnelles

Les limites sont des seaux à jetons par processus :

- Appels sans identité Discord vérifiée : réserve de 240, recharge de 4 par seconde, par adresse réseau directement vue par l’application.
- Connexion OAuth : réserve de 120, recharge de 2 par seconde, par adresse réseau.
- Appels d’un joueur vérifié : réserve de 60, recharge de 4 par seconde, par compte, partagée entre ses appareils.

Une saturation renvoie HTTP 429 et Retry-After, sans traitement de l’action. Derrière un proxy, plusieurs joueurs peuvent partager la même adresse vue par l’application pour les étapes anonymes/OAuth ; les réserves initiales permettent un afflux raisonnable. Les limites des joueurs vérifiés restent individuelles. Les tests du limiteur utilisent volontairement des réserves réduites pour vérifier son comportement rapidement.

Ces quotas réduisent les abus ; ils ne remplacent pas une protection de débit au niveau du proxy et ne garantissent pas une résistance à une attaque distribuée. Ils ne suppriment pas automatiquement les anciennes sessions de la base. Aucun test de charge massif en production n’a été effectué.

## Contrôles existants revérifiés

- L’identité vient de la réponse OAuth Discord vérifiée, pas d’un ID, nom ou avatar envoyé par le client. Les tokens de session sont opaques et stockés sous forme de condensat.
- Le panel Activity vérifie les IDs Discord autorisés côté serveur. Masquer ou afficher un bouton ne suffit pas à obtenir l’accès. Les modifications admin vérifient le montant attendu et la référence de l’opération, puis sont journalisées.
- Les montants, résultats, récompenses et mises sont calculés ou validés côté serveur. Les références d’opérations et révisions empêchent les rejeux et doubles paiements testés ; transactions et reprises après interruption restent couvertes.
- Les cartes cachées, le paquet et la position dangereuse de la roulette russe ne sont pas transmis dans l’état public actif. Les tirages financiers utilisent le générateur fondé sur l’aléa système.
- Les achats et identifiants SQL dynamiques inspectés sont limités par des listes autorisées ; les valeurs sont liées aux requêtes. L’accès aux fichiers publics vérifie que le chemin résolu reste dans le répertoire public.
- La recherche ciblée de formats de tokens Discord, webhooks et clés privées n’a trouvé aucun motif dans 409 fichiers texte inspectés. Ce contrôle ne prouve pas l’absence de tous les formats de secrets possibles.

## Dépendances

L’audit npm du verrouillage actuel ne signale aucune vulnérabilité connue. Le premier audit du runtime Python a signalé multidict 6.7.1. Après passage à 6.9.1, l’audit des 12 dépendances Python du service réellement présentes dans l’environnement de vérification ne signale plus de vulnérabilité connue. La vérification des contraintes installées est également réussie.

Source primaire de la correction : [avis des mainteneurs multidict GHSA-54p9-h82j-f925](https://github.com/aio-libs/multidict/security/advisories/GHSA-54p9-h82j-f925), versions affectées 6.7.0 à 6.9.0, correction 6.9.1. La fuite concerne certaines unions/soustractions de vues items de l’extension C, pas toute lecture d’en-tête HTTP. Les résultats des scanners décrivent les avis connus au moment de cette vérification, pas les versions actuellement installées sur votre serveur.

## Vérifications

- 362 tests serveur réussis, dont 16 nouveaux tests de sécurité.
- 162 tests client et 17 tests bot réussis : 541 tests automatisés au total.
- Compilation Python, contrôle Pyflakes sans alerte, TypeScript et build Vite réussis.
- Trois parcours navigateur réussis : cookie partitionné en iframe HTTPS (10 contrôles), panel admin PC/mobile (38 contrôles), tutoriel PC/mobile (24 contrôles). OAuth est simulé dans ces essais locaux ; aucun véritable secret Discord n’y est utilisé.

Les 16 nouveaux tests couvrent notamment : expiration d’une session admin, refus du token expiré, migration sans reset, redémarrage sans prolongation, rotation, reconnexion avec le même Gold, saturation et recharge du quota, mémoire bornée, cookies et en-têtes forgés, OAuth mal formé, POST sans session, corps trop volumineux et cache privé.

Les fichiers RESULTATS_SECURITE_20261021.json détaillent les résultats. Le bundle Vite conserve son avertissement de taille, sans erreur de compilation.

## Installation

Copier les fichiers du projet complet ou le contenu de la mise à jour légère à la racine du dépôt, puis reconstruire et redéployer sur Coolify avec le Dockerfile existant. La reconstruction réinstalle les dépendances Python avec la nouvelle contrainte de sécurité. Ne pas se limiter à un redémarrage de l’ancienne image.

Conserver les secrets, le volume ACTIVITY_DB et PORT=10080. Aucun reset de compte, prix, bonus de tutoriel ou changement de design n’est ajouté. Aucun déploiement n’a été lancé depuis cet audit.

Le partage réel du Gold avec Oddium n’est pas testé ici : cette archive utilise toujours l’économie SQLite isolée et refuse ECONOMY_DATABASE_URL, comme indiqué dans le README existant. Les permissions réelles du bot, secrets et versions de l’image déjà déployée restent hors de portée de cet audit local.
