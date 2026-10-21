# Audit Altherya — 21 octobre 2026

## Bilan

Audit du code de l’archive complète après le correctif de mise de l’arène. Plusieurs chemins d’abus et erreurs ont été corrigés directement. Les résultats concernent le code et les bases temporaires testés ici ; ils ne constituent pas une garantie d’absence de toute faille et ne certifient pas le serveur en production.

**Point important : le Gold partagé avec Oddium n’est pas opérationnel dans cette branche.** `Activity.__init__` refuse explicitement `ECONOMY_DATABASE_URL` et les actions utilisent une base SQLite locale. Je n’ai pas supprimé cette protection ni tenté une migration PostgreSQL, qui pourrait désynchroniser les soldes. Les contrôles de conservation et de persistance du Gold ci-dessous concernent SQLite.

## Problèmes corrigés

| Référence | Priorité | Problème confirmé | Correction |
|---|---|---|---|
| A01 | Haute | Annulation d’un blackjack ou d’une roulette russe après révélation, avec restitution de la mise | L’API refuse l’annulation d’une manche engagée. Il faut aller jusqu’au résultat. Les remboursements des écrans de choix non révélés du bot historique restent permis. |
| A02 | Haute | L’expiration de l’accès clandestin permettait de rembourser une main défavorable | Une manche déjà engagée reste jouable après expiration ; aucune restitution automatique après révélation. Le blackjack affiche encore ses actions. L’accès reste contrôlé pour les nouvelles mises. |
| A03 | Moyenne | Les combats de quête pouvaient coexister avec une partie ou un combat d’arène ; changement de techniques possible pendant une quête | Vérification serveur commune des activités en cours, dans la transaction de l’action. Le grimoire bloque aussi les changements pendant un combat de quête. |
| A04 | Haute en cas de mauvaise configuration | Une seule des deux variables OAuth définie activait involontairement le parcours anonyme | La présence de l’une des variables impose désormais une identité Discord vérifiée. Le mode local sans aucune variable reste disponible pour les tests. |
| A05 | Faible | Un POST refusé pour absence de protection CSRF créait d’abord une session et un personnage | Refus avant initialisation ou création de session. |
| A06 | Faible | Les indices de chapitre étaient convertis, acceptant notamment booléens et nombres décimaux | Type entier strict et chapitre existant exigés. |
| A07 | Moyenne | Variable `branch_total` non définie dans l’annonce de succès attribué par un administrateur du bot historique | Calcul du nombre de succès de la branche avant l’affichage. |
| A08 | Moyenne | Retour de l’identification du bot historique vers une classe inexistante | Retour vers le menu d’accueil existant et contrôle du propriétaire de l’interaction. |

La faille A01 a également été fermée dans les vues historiques : les délais expirés de blackjack/roulette russe et l’abandon volontaire de roulette russe soldent la manche à zéro au lieu de rembourser une mise déjà révélée. Le bouton d’abandon indique la perte de la mise. Ces chemins ont été testés avec des objets Discord simulés, sans envoyer de messages.

Nettoyage complémentaire : suppression d’une clé `ends_at` en double et d’un import inutilisé. Deux tests navigateur historiques ont été adaptés : le parcours de taverne avait changé et les captures prises pendant la course faussaient la mesure de temps. Le test du timer de contrat attend désormais un changement réel pendant au plus quatre secondes, au lieu de supposer que le premier tick intervient après exactement 1,1 seconde. Aucun décor, prix d’outil, récompense de tutoriel ou règle de récompense n’a été refait.

## Couverture des fonctions

| Domaine | Contrôles effectués | Résultat et limites |
|---|---|---|
| Connexion / sessions | OAuth côté serveur, cookies, changement de compte, conservation des sessions, protection CSRF | Tests locaux réussis ; connexion réelle via Discord non rejouée |
| Tutoriel | Étapes obligatoires, récompense unique, replay et identité canonique multi-appareil | Tests serveur réussis ; bonus conservé |
| Administration | Liste des trois ID autorisés, refus des autres joueurs, recherche des tutoriels terminés, modifications Gold/XP, historique et doublons | Tests serveur réussis ; aucun appel admin en production |
| Banque | Valeurs négatives, booléens, décimaux, dépassement du solde, frais, dépôts simultanés, répétition de la même opération | Conservation de fortune et idempotence testées |
| Marchand / inventaire | Achat unique, vente de quantité exacte, survente refusée, séparation des objets d’histoire et chapitres | Tests client/serveur réussis |
| Forge classique / KHAZ’GORAM | Niveau, ressources, Gold/Pouciels, équipement existant, révision et modification pendant combat | Tests réussis ; prix conservés |
| Arène | Dix champions, intentions, riposte, PV, résultat et paiement uniques, techniques volées, mise 0–500, double clic | Tests client/serveur et navigateur réussis ; combat sans mise existant conservé |
| Tour d’Ashkar | Niveau 5, ordre des étages, trois validations par jour, reprise, replay sans récompense supplémentaire, techniques des boss tous les dix étages | Tests serveur réussis ; contenu actuel limité aux dix étages présents |
| Grimoire | Couverture, ouverture, sommaire, page par technique, verrouillages, quatre emplacements, révisions, combat actif | Tests client/serveur réussis ; design conservé |
| Taverne / boissons | Réputation, boissons verrouillées, nombre quotidien, cooldown | Tests serveur réussis |
| Jeux de taverne | Dés, pile ou face, pierre-feuille-ciseaux, résultats serveur, mise et paiement | Tests client/serveur et navigateur |
| Salle clandestine | Accès initial, expiration pendant une manche, mises maximales et fonds | A01/A02 corrigées ; accès réel aux salons non testé |
| Jeux clandestins | Blackjack, roulette, rouleaux, courses et roulette russe : résultats serveur, données cachées, animation et règlement | Tests client/serveur et navigateur ; détail des dernières passes plus bas |
| Ruelle | Larcin, cibles PNJ, réputation, vigile, braquage, code non exposé et nombre d’essais | Tests client/serveur réussis |
| Petites annonces | Huit offres, rang tiré après acceptation, contrat unique, délai serveur, récompense non anticipée/non répétée | Tests serveur et menu client ; parchemin conservé |
| Histoire principale | Ordre des objectifs, niveaux, indices/puzzles, ressources livrées, expéditions, délai, récompenses uniques | Tests serveur réussis ; exclusion des combats simultanés corrigée |
| Quêtes quotidiennes | Tirage persistant, variété, familles autorisées, absence d’amélioration de forge dans le tirage, récompense unique | Tests serveur réussis |
| Profil / château / podium | Nom du serveur, avatar avec repli, progression et lecture du classement | Tests client/serveur et navigation |
| Monde / hub | Carte et destinations, boutons, accès aux scènes, menus PC/mobile | Navigation automatique sur quatre tailles d’écran |
| Gazette / logs / portail | Filtrage des mentions, outbox, répétitions, erreurs, restauration du portail, noms serveur | Tests automatisés avec réseau Discord simulé ; livraison réelle non vérifiée |
| Sauvegardes | Transactions, rollback après panne, crash de processus, reprise, sauvegarde SQLite vérifiée et restauration | Tests serveur réussis sur fichiers temporaires |

## Vérifications réalisées

- Compilation des 100 fichiers Python présents, modules et tests compris : réussie.
- Compilation TypeScript et build Vite : réussis. L’avertissement de bundle supérieur à 500 ko demeure.
- Suite client : **170 tests réussis**.
- Suite serveur complète exécutée pendant l’audit : **288 tests réussis**.
- Dernière passe ciblée après les derniers correctifs : **12 tests réussis**, comprenant des cas déjà inclus dans la suite précédente. Ces nombres ne doivent pas être additionnés comme des tests uniques.
- Recherche statique : les deux noms non définis identifiés ont été corrigés. Il reste des avertissements de maintenance dans les modules historiques (imports/variables inutilisés et redéfinitions de classes). Ils ne sont pas présentés comme des plantages confirmés et n’ont pas été supprimés aveuglément.
- 84 chemins d’assets statiques cités littéralement : aucun fichier manquant. Les chemins construits dynamiquement sont couverts partiellement par les tests de jeux et ne sont pas tous certifiés par ce scan.
- Archive source : aucun fichier `.env` réel, fichier de clé privée ou base de données inclus ; aucun candidat de token Discord détecté par les motifs recherchés. Cette recherche ne détecte pas tous les formats possibles de secret.
- `npm audit` sur le lockfile : **0 vulnérabilité connue signalée**.
- `pip-audit` sur une résolution neuve des dépendances de l’API : **12 paquets, 0 vulnérabilité connue signalée**. Cela ne certifie pas les versions déjà déployées, le système Docker ni les dépendances complètes du bot historique.

### Passes navigateur

Chromium local, API réelle locale et bases temporaires, sans appels Discord réels. Les captures servent uniquement à l’inspection interne.

| Scénario | Dernière passe |
|---|---|
| Navigation hub, lieux et ruelle | 56 vérifications réussies, 4 formats |
| Banque, livre du troubadour et contrats | 49 vérifications réussies, 4 formats |
| Arène et sélecteur de mise | 40 vérifications réussies, 4 formats |
| Blackjack | 32 vérifications réussies, 4 formats |
| Machine à sous | 24 vérifications réussies, 2 formats et arrêts successifs mesurés |
| Roulette | Réussie, 6 formats |
| Courses de chevaux | Réussies, 4 formats ; environ 9,85 à 9,92 s mesurées avec la requête |
| Roulette russe | Réussie, 4 formats |
| Dés | Réussis, 4 formats |
| Pile ou face | Réussi, 4 formats |
| Pierre-feuille-ciseaux | Réussi, 4 formats |

Les tailles comprennent 1440×900, 1186×570, 390×844 et 320×568 selon les scénarios ; la roulette couvre six formats. Les tests des rouleaux vérifient aussi leur arrêt successif de gauche à droite. Les tests de courses contrôlent classement et Gold, déplacement, images de galop et durée ; la présentation existante reste d’environ 9,4 secondes, hors délai de requête serveur.

## Points restant à traiter ou vérifier

1. **Gold commun Oddium : absent de cette branche**, comme indiqué en tête. Préparer une intégration dédiée avec identités Discord canoniques, transactions et règles de migration ; ne pas simplement retirer le garde-fou actuel.
2. **Protection contre la surcharge : non certifiée.** Aucune limitation de débit globale n’est définie dans le serveur de l’application ; une partie des lectures/écritures SQLite est synchrone. La configuration anti-abus du reverse proxy et la tenue en charge réelle doivent être vérifiées. Aucun test de charge n’a visé ton domaine.
3. **Une seule instance active par base SQLite.** Le démarrage rembourse les parties interrompues et les vues historiques conservent aussi de l’état en mémoire. Le fonctionnement de plusieurs processus/conteneurs simultanés sur la même base n’est pas garanti. Éviter un chevauchement d’instances lors du déploiement.
4. **Persistance Coolify : à contrôler sur le serveur.** Le volume doit bien conserver la base et les copies de sauvegarde après reconstruction. Les tests de restauration locaux réussissent, mais l’existence et la restauration des sauvegardes de production n’ont pas été vérifiées.
5. **Discord réel :** permissions des salons, diffusion Gazette/Hall/Logs, portail et rendu dans les clients Discord PC/mobile restent à confirmer après déploiement. Les navigateurs locaux ne remplacent pas ces essais.
6. **Bot historique complet :** analyse statique et tests ciblés des fonctions modifiées, sans démarrer son client Discord, son OCR, ses bibliothèques de rendu ni toutes ses anciennes commandes. Le Dockerfile principal lance l’API Activity ; le bot historique constitue un point d’entrée distinct.
7. **Maintenance :** bundle client volumineux, avertissements statiques historiques et volume croissant des reçus/logs à surveiller. Aucun reçu d’idempotence ni historique joueur n’a été effacé pour masquer ce problème.

## Installation du correctif

Décompresser l’archive MAJ et copier le contenu de `Altherya_V0_8_10` dans la racine actuelle du projet en remplaçant les fichiers correspondants. L’archive complète contient également tous les fichiers et assets précédents. Reconstruire et redéployer via la procédure habituelle ; aucun fichier de données ni secret n’est fourni et aucune migration manuelle n’est requise pour ces correctifs.

Les paramètres du serveur et les données réelles n’ont pas été modifiés. Pour le bot historique, un délai expiré après révélation de la main est désormais une perte de mise, ce qui ferme l’abus de remboursement volontaire.
