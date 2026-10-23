# Quêtes dans le monde d’Altherya — 23 octobre 2026

## Fonctionnement intégré

Les 32 quêtes de la campagne ont une destination réelle pour chaque étape. Les quêtes se prennent auprès du commanditaire et se rendent sur place. Les dialogues, décisions, remises de ressources, rapports et combats ne sont plus exécutables depuis le carnet.

Le carnet devient un suivi des objectifs, des destinations, des objets de quête et des preuves. Le suivi à droite permet de rejoindre la scène indiquée ; il n’accomplit pas l’objectif à votre place.

Les six lieux illustrés existants sont intégrés à la navigation : Bureau des convois depuis le marché, Archives depuis la banque, Halte de la Lisière depuis Elarwyn, Atelier des sceaux depuis KHAZ’GORAM, Relais de la Pierre Fendue depuis Vorak, Belvédère depuis Ashkar. Les entrées restent conditionnées au niveau et à la progression. Thorgar et Ashkar disposent également de scènes dans ce parcours.

Les points d’enquête sont placés sur les éléments des décors existants : registres, comptoirs, caisses, borne, traces, établi et panorama. Les missions de terrain nouvellement acceptées demandent des interactions dans la scène : témoins, balises, évacuation ou sécurisation. Leurs durées et les durées d’analyse restent applicables.

Quatre accessoires d’enquête sont conservés dans un sac séparé des ressources commerciales : double du reçu, attestation de la banque, plaque de transport et fragments du journal. Leur découverte est enregistrée une seule fois ; leur remise au destinataire est enregistrée. Ils ne sont pas ajoutés au stock échangeable. La plaque des nouvelles quêtes se prend directement sur la caisse à la Lisière, sans lancer un timer de collecte, puis doit être apportée au forgeron. Le rapport destiné au château n’est plus présenté comme une analyse chez Thorgar dans les nouvelles missions concernées.

Les services habituels des lieux restent accessibles avec leur bouton dédié. Un échange de quête affiche le décor du personnage derrière le dialogue. Les commandes de la scène sont suspendues pendant cet échange. Les suivis latéraux se replient lors d’une recherche de terrain pour laisser le décor accessible.

## Sauvegarde et contrôles

Deux nouvelles tables sont créées automatiquement : position d’interaction de quête et objets d’enquête. Aucun reset des joueurs, des étapes, des choix ou des récompenses versées.

Chaque action de quête vérifie la destination enregistrée côté serveur, un jeton renouvelé lors du déplacement, l’identité de la quête et sa révision. Les recherches, travaux, livraisons, délais et combats conservent leurs contrôles. Les tentatives à distance, jetons périmés ou empruntés, double collecte et double paiement sont testés. Les fermetures administrateur s’appliquent au lieu concerné ; fermer les quêtes ne ferme pas tous les déplacements ordinaires.

Les anciennes quêtes déjà acceptées gardent leurs étapes et durées ; elles passent désormais par les lieux. Les actions de terrain supplémentaires et les corrections de destination s’appliquent aux nouvelles acceptations (édition 6). Les récompenses figées à l’acceptation restent conservées. Les quêtes déjà terminées ne sont pas réinitialisées et ne peuvent pas être repayées. Les quêtes quotidiennes continuent de suivre les activités habituelles du jeu.

## Vérifications

- Compilation TypeScript et production Vite réussies ; avertissement existant de taille du bundle.
- Compilation Python API et bot réussie.
- 215 tests d’interface réussis, comprenant carnet en lecture seule, dialogues locaux, contrôles de combat, actions dans les scènes, rapports et journal des mises à jour.
- 113 tests serveur réussis : campagne, contrôles des lieux, objets, actions de terrain, port, administration et courrier.
- 38 contrôles navigateur sur l’application complète compilée et une API locale réelle, en 1440×900 et 390×844 : ouverture depuis le hub, enquête, retour au marchand, sauvegarde après rechargement, travaux de terrain et récupération de la plaque. Aucune erreur JavaScript relevée.
- Deux parcours ordonnés de 32 quêtes réussis, avec les deux séries de décisions. Horloge virtuelle pour les délais ; XP externe injectée uniquement aux paliers de niveau ; ressources et Gold obtenus par les actions normales. Aucune étape, victoire, récolte ou récompense de quête injectée. Les résultats détaillés sont joints.

Ces contrôles utilisent des joueurs et bases temporaires. La session Discord Activity et le serveur de production n’ont pas été déployés ni manipulés. Ils ne remplacent pas une vérification après votre redéploiement.

## Installation

Mise à jour cumulative à appliquer au projet existant. Copier le contenu de Altherya_V0_8_10 dans le projet, accepter les remplacements et inclure les nouveaux fichiers, puis reconstruire et redéployer. Conserver la bibliothèque complète d’assets déjà installée, les données, le .env et les variables Coolify. Les décors et accessoires utilisés sont ceux déjà présents dans le projet ; aucun téléchargement d’images supplémentaire n’est nécessaire.
