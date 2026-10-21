# Altherya — vérifications étendues et correctifs

Date : 21 octobre 2026. Périmètre : archive complète Altherya, Activity et moteurs SQLite locaux. Aucun serveur réel, compte joueur réel ou salon Discord n’a été modifié.

Il est impossible de réaliser « tous les tests possibles » : les séquences d’actions, conditions réseau et états possibles sont illimités. Cette passe élargit concrètement les deux audits précédents, corrige les problèmes reproduits et conserve les limites ci-dessous.

## Résultats

- **346 tests serveur réussis**, dont **26 nouveaux tests** de résilience, entrées malformées, bonus, sauvegardes et cohérence. Ces nombres se recouvrent.
- **17 tests historiques du bot réussis**. Plusieurs vérifient la structure du code ou des fonctions isolées ; ils ne remplacent pas un démarrage du bot connecté à Discord.
- **173 tests client réussis**, compilation Python et build TypeScript/Vite réussis. L’avertissement existant sur la taille du bundle demeure.
- **28 parcours navigateur réussis après corrections**, avec tailles PC/mobile selon les scripts : huit jeux, navigation de la cité, ruelle et braquage, arène, tour/grimoire, banque/livre/parchemin, forge, annonces, campagne et suivis, profil/surnoms/admin, tutoriel, démarrage, animations du hub et cookie en iframe HTTPS. Les parcours concernés ont été relancés après leurs corrections. Les huit jeux ont été parcourus ; chaque script ne couvre pas tous les appareils et toutes les issues possibles.
- **10 800 scénarios de combat** : 180 combinaisons de techniques équipables, niveaux 1/10/30, dix profils de champions et équipement d’attaque légendaire présent/absent. Jusqu’à quatre tours avec actions définies, vérification des bornes et de la sérialisation. Ce n’est pas une exploration de toutes les stratégies possibles.
- **732 mutations de requêtes** dans deux matrices (180 et 552 cas) : soldes invariants sur la première, absence d’erreur interne non gérée sur la seconde. Certains champs supplémentaires sont volontairement ignorés ; tous les cas ne parcourent pas toutes les branches métier.
- Un mois de récompenses quotidiennes puis le même calendrier parcouru en sens inverse : 30 versements, aucune deuxième récompense pour une date déjà payée.
- Charge HTTP locale : 16 personnages, 320 opérations bancaires et 320 lectures ; **640 réponses réussies**, soldes attendus, contrôle SQLite `integrity_check` réussi.
- Simulation des probabilités relancée : un million de tirages synthétiques et exploration des cotes des chevaux. Le générateur reproductible de cette simulation est distinct de l’aléatoire système utilisé en jeu.
- Les suites existantes couvrent aussi la campagne de 32 quêtes, les niveaux et lieux verrouillés, les objets, les achats/ventes, les améliorations, les annonces, les récompenses uniques, le tutoriel, les identités et les droits admin.

## Corrections livrées

### 1. Une partie défavorable ne peut plus être effacée par le redémarrage de l’Activity

Avant : une partie persistée mais encore active était remboursée au démarrage. Un joueur ayant vu une mauvaise main pouvait profiter d’un redémarrage planifié pour éviter sa perte. Aucun moyen de provoquer à distance un redémarrage n’a été démontré.

Maintenant : les parties de blackjack, roulette russe et arène dont l’état est exploitable reprennent avec la même mise, les mêmes cartes, le même barillet, les mêmes PV et les mêmes effets. La reprise est liée à la session moteur, son propriétaire, son type et son montant. Le redémarrage n’ajoute ni Gold ni XP.

Les sessions orphelines ou inutilisables conservent leur remboursement unique. La récupération s’exécute dans une transaction : une interruption ne peut pas conserver seulement une partie des remboursements. L’ancien reset ponctuel des champions reste compatible et annule les combats antérieurs lorsqu’il doit réellement s’appliquer. Aucun nouveau reset de progression n’est ajouté.

Les fonctions historiques de récupération du bot gardent leur comportement par défaut. Le changement de reprise concerne l’Activity persistante ; un ancien bot aux parties uniquement en mémoire n’acquiert pas cette persistance par cette mise à jour.

Tests : main perdante puis plusieurs redémarrages et accès expiré ; même barillet après chaque tour ; combat et mise conservés ; sessions orphelines ; état incomplet ; récupération interrompue ; lecture dans un nouveau processus ; arrêt réel du processus après débit et après calcul/paiement ; rejouage de la même opération après reprise ; quatre processus ouvrant le même personnage avec une partie active.

### 2. L’état affiché provient d’une seule transaction

Avant : un état complet du joueur déclenchait de nombreuses connexions et validations disque indépendantes. Des mises à jour concurrentes pouvaient aussi intervenir entre les différentes lectures.

Maintenant : assemblage de l’état et rapprochement des récompenses utilisent une connexion et une transaction communes. Les moteurs conservent leurs points de sauvegarde locaux ; la transaction extérieure décide du commit. Un échec pendant l’assemblage annule également le rapprochement commencé.

Deux contrôles dédiés vérifient qu’une lecture interrompue ne verse pas une expédition à moitié et que niveau, XP du niveau et XP totaux restent cohérents pendant des attributions concurrentes.

Mesure locale avec le même script et les mêmes soldes attendus : environ **163 secondes avant, 17 secondes après** pour 640 requêtes. Médiane POST : environ 5 250 ms avant et 560 ms après ; p95 : environ 7 294 ms et 957 ms. Des suites navigateur partageaient la machine : ces chiffres indiquent le coût local observé, pas une capacité garantie ni un benchmark de production.

### 3. Le suivi des quêtes laisse de l’espace aux boutons inférieurs du hub

La hauteur des panneaux illustrés pouvait empiéter sur « Mon profil ». Leur hauteur réserve maintenant une bande inférieure. Les positions des boutons et le dessin des menus restent conservés. Sur une largeur de tablette (jusqu’à 1 100 px), les suivis commencent repliés, sauf préférence explicite déjà enregistrée. Les panneaux latéraux restent repliables pour accéder aux lieux situés derrière eux.

Les parcours réels ont également révélé des tests visant les anciens boutons, l’ancien profil, l’ancien ratio d’image ou l’ancienne présentation des annonces. Ils sont adaptés aux composants actuels. Le test de panne du tutoriel tient compte des deux tentatives réseau automatiques : il provoque deux échecs POST, sans consommer l’injection sur une lecture périodique.

### 4. Le profil redonne accès au tutoriel

La nouvelle présentation du profil avait perdu son bouton de relecture. « Refaire le tutoriel » est rétabli dans le pied du profil et de l’inventaire, avec les boutons du même style. Cette action ouvre le parcours de relecture existant ; elle ne modifie pas la récompense initiale et n’ajoute aucun nouveau versement. Un test client dédié vérifie le routage et l’absence de changement des données du personnage.

## Ce qui a été vérifié sans modifier les règles

- Les bonus temporaires testés ne s’accumulent pas à chaque rechargement et le catalogue de techniques reste inchangé.
- Les bonus Gold x2 des jeux doublent le bénéfice, pas la mise remboursée. Un double au blackjack utilise bien la mise augmentée ; une égalité ou une perte ne crée pas de bénéfice.
- Un résultat déjà payé n’est pas payé une deuxième fois après changement d’événement ou rejouage de la requête.
- Les bonus d’équipement additionnent les pièces des emplacements attendus. Les restaurations testées ne multiplient pas les PV.
- Les requêtes trop grandes, le JSON invalide et les tentatives d’accès admin sans identité autorisée sont rejetés dans les cas testés.
- Une base identifiée comme corrompue n’est pas écrasée au démarrage. Un échec de synchronisation d’une nouvelle copie de sauvegarde laisse la copie vérifiée précédente intacte et supprime le temporaire.
- Le modèle bancaire de 2 000 opérations, les rafales concurrentes, les reçus de récompenses, les contrôles de versions et la cadence serveur des jeux restent validés par la suite complète.

Aucun prix d’outil, bonus initial du tutoriel (100 Gold / 25 XP), montant d’armure validé, probabilité, gain ou design approuvé n’a été rééquilibré. Les effets livre du troubadour et parchemin des annonces sont conservés.

## Limites et validations encore nécessaires

- Aucun audit ne prouve l’absence de toute faille. Pas de preuve formelle, de couverture exhaustive des chemins, de test de toutes les stratégies de blackjack ou de tous les calendriers et combinaisons d’équipements.
- Les navigateurs sont des Chromium automatisés avec tailles PC/mobile et, selon les parcours, iframe HTTPS et préférences d’animation. Ce ne sont pas des appareils physiques, Brave, Safari/iOS ou une session Discord réelle.
- OAuth, noms de serveur, avatars et événements Discord sont vérifiés localement avec réponses simulées ou cas d’erreur. Permissions, jetons réels, publication des logs, portail et lancement dans le serveur Discord restent à valider sur place.
- La charge est locale et limitée à 16 personnages. Elle ne valide ni les capacités de Coolify/Nginx, ni une attaque DDoS, ni des milliers de joueurs simultanés. L’API utilise encore des accès SQLite synchrones ; la limitation globale des requêtes et l’architecture pour une très forte charge restent à traiter séparément.
- Les arrêts forcés utilisent une terminaison réelle de processus, pas une panne matérielle du disque. La corruption testée et l’erreur de synchronisation injectée ne couvrent pas tous les modes de panne physique.
- **L’Activity reste volontairement en SQLite isolé** et refuse `ECONOMY_DATABASE_URL`. La connexion à l’économie partagée Oddium/PostgreSQL n’a pas été réalisée ni validée ici.
- Les contrôles de dépendances de l’audit précédent n’ont pas été transformés en garantie contre de futures vulnérabilités. Aucune nouvelle dépendance n’est ajoutée.

## Installation et reproduction

La version complète contient tous les assets existants et les correctifs cumulés. Le petit ZIP est une mise à jour cumulative de code et de tests : fusionner son dossier `Altherya_V0_8_10` avec celui du projet. Ne pas remplacer les sauvegardes par des bases de test : aucune base n’est fournie.

Reconstruire le client et redéployer/redémarrer normalement l’Activity pour appliquer le code. Aucun déploiement réel n’a été effectué pendant cet audit. Il n’est pas nécessaire de réinitialiser les joueurs ou le tutoriel.

Depuis la racine du projet : `python3 -m unittest discover -s apps/api/tests -v`. Dans `apps/bot/tourwork` : `python3 -m unittest discover -s tests -v`. Dans `apps/game` : `npm test`, puis `npm run build`. Les parcours `tests/browser-*.cjs` requièrent Chromium/Playwright et un environnement de test sans jeton Discord réel. Les anciens tests de versions antérieures qui ne sont pas listés dans les résultats ne sont pas présentés comme validés.

`RESULTATS_VERIFICATIONS.json` donne les résultats structurés, les parcours exécutés et les mesures de charge. Les captures de diagnostic et bases temporaires ne sont pas incluses.
