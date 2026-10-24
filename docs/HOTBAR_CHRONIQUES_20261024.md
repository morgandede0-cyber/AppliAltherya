# Hotbarres et Chroniques d’Altherya

## Contenu intégré

Le style validé des médaillons discrets est appliqué au haut et au bas de l’écran. L’identité utilise le nom et la photo du serveur Discord lorsqu’ils sont disponibles ; les valeurs de niveau, XP, portefeuille, banque et courrier viennent du snapshot réel.

Le portrait ouvre le profil. Les cinq médaillons du bas ouvrent Monde, Quêtes quotidiennes, Chroniques, Inventaire et Petites annonces. Les quotidiennes ouvrent le panneau existant (pas une deuxième liste). Inventaire ouvre directement le vrai sac du joueur. Les accès portables correspondants en doublon sont retirés des contrôles du hub ; les autres enseignes et l’accès admin restent à leur emplacement.

« Les Chroniques d’Altherya » présente deux volumes :

- « La Destinée d’Altherya » : les 32 quêtes principales existantes, sommaire par saison, consultation de la quête courante et relecture des missions dont le serveur possède un reçu de fin.
- « Les Récits du Royaume » : les chroniques existantes du troubadour, avec leurs objets à réunir et leur déblocage réel. Ce volume reprend ce contenu secondaire existant ; il n’ajoute pas de nouvelles missions ni de nouveaux paiements. Le livre du troubadour et son effet de lecture sont conservés.

Les pages futures apparaissent scellées. Le serveur ne publie pas leurs résumés, objectifs ou solutions ; les conditions de niveau restent visibles. L’accès à la lecture d’une page n’accepte ni ne valide une quête. Rencontres, recherches, objets et remises restent dans les lieux d’Altherya, avec les vérifications existantes.

Les pages se tournent avec une animation de 560 ms, protégée contre les clics répétés et désactivée en réduction des animations. Les temporisateurs sont nettoyés à la fermeture. Une actualisation conserve les positions de lecture et le bouton focalisé. Un changement de compte ferme la lecture précédente.

## Explications des quêtes

Contexte du scénario, objectifs, destination et récompense réelle sont affichés. Une piste adaptée au type d’étape explique comment chercher : comparer des témoignages, examiner le décor, préparer un voyage, consulter les indices déjà recueillis. Elle ne donne ni réponse de code, ni solution d’énigme, ni coordonnées cachées. Les preuves consultables sont celles déjà découvertes.

## Visuels et provenance

Production avec l’outil intégré de génération d’images. Fonds des deux livres et du livre ouvert nettoyés depuis les images validées : suppression des seuls textes, informations et contenus des pages ; conservation des couvertures, matériaux, cadres et décor. Les textes, valeurs et commandes sont rendus par le jeu.

- `assets/chronicles/library-blank.png` : deux volumes vierges.
- `assets/chronicles/book-blank.png` : double page vierge.
- `assets/chronicles/contents-art.png` : illustration du sommaire validé, découpée par fenêtre SVG.
- `assets/chronicles/sealed-page.png` : lettre scellée validée, seule la lettre est affichée par fenêtre SVG.
- `assets/hotbar/world.png`, `daily.png`, `inventory.png` : médaillons isolés, fond transparent, carte/parchemin/sac, bronze patiné assorti à la troisième hotbarre validée.
- `assets/hotbar/chronicles.png`, `jobs.png` : médaillons approuvés livre-couronne-épées et panneau d’annonces, conservés.

## Installation

Mise à jour cumulative à copier sur le projet existant en remplaçant les fichiers, puis reconstruire et redéployer le frontend et l’API dans Coolify. Conserver base, sauvegardes et variables d’environnement. Le décor réel du hub est conservé ; celui des exemples de hotbarre n’est pas substitué au monde.

La remise à zéro unique du tutoriel de la livraison précédente reste active avec la même révision : cette mise à jour ne la relance pas une seconde fois. Les reçus de récompense, Gold, XP, prix des outils, paliers et sauvegardes ne sont pas modifiés.
