# Les quêtes principales sont intégrées — 17 octobre 2026

## Jouer
Après le tutoriel, ouvrir le panneau de droite, onglet Aventure, puis « Ouvrir la quête ». Accepter la mission, lire les échanges et accomplir ses trois objectifs dans l’ordre. Les chroniques officielles restent accessibles dans l’onglet Chroniques. Les quotidiennes aléatoires restent à gauche.

Le journal accueille les rencontres du scénario, avec les images existantes des lieux et personnages quand elles sont disponibles. Il contient les dialogues, les choix, les enquêtes, les missions de reconnaissance et les combats du récit. Aucune nouvelle carte avec déplacement libre n’est ajoutée.

## Contenu jouable
Quatre saisons, seize chapitres et trente-deux quêtes principales : Les contrats de Legacy, La piste de Seraph, Les repères d’Ashkar, Le prix du passage. Les huit propositions de quêtes secondaires du document de scénario ne sont pas incluses dans cette campagne principale.

Les preuves sont conservées par la progression du journal et ne se mélangent pas aux objets vendables. Les achats d’histoire et les trente chapitres officiels restent conservés, dans leur parcours séparé. Les conversations et décisions proposées ont été adaptées au jeu actuel ; les notes de conception ne sont pas affichées comme des dialogues.

Les missions d’observation d’Ashkar sont des rencontres narratives du journal, accessibles au niveau requis. Elles ne valident pas les étages des combats de la tour. L’accès final du récit passe par la Faille Rouge, niveau 10, sans débloquer la Cime réservée au niveau 30.

## Difficulté et récompenses
- Prérequis progressifs entre niveaux 1 et 10. Les activités ordinaires restent nécessaires pour progresser.
- Enquêtes de 15 à 30 minutes, reconnaissances de 30 à 75 minutes. Les délais sont sauvegardés et continuent hors connexion ; on peut pratiquer les autres activités pendant l’attente.
- Voyages réellement terminés vers les destinations demandées. Ils doivent commencer après l’activation de leur objectif. Leurs règles de matériel, de niveau et de butin restent celles du jeu.
- Livraison de cinq Bois de chêne à Thorgar : les matériaux sont réellement prélevés, une seule fois.
- Questions fondées sur les indices ; une erreur impose une minute de préparation avant une nouvelle tentative.
- Combats résolus par le moteur existant : techniques, ripostes, PV, recharge et logs. Une défaite permet de retenter après une minute, sans perdre les preuves.
- Pas de Gold ni d’XP versés à chaque tentative de combat. La récompense arrive une seule fois, à la remise de la quête complète.

La campagne distribue au total 8 105 Gold et 1 505 XP, répartis selon les difficultés et les fins de saison. Le boss final vaut 600 Gold et 100 XP. La récompense annoncée dans le journal est fixe pour la campagne. Voir CAMPAGNE_RECOMPENSES.md pour les trente-deux lignes de détail.

Les décisions sont sauvegardées. Le secours direct des convoyeurs facilite une interception ultérieure ; le choix du leurre ou du barrage modifie l’adversaire de cette interception ; le dernier choix détermine le sort du Faussaire dans l’épilogue personnel. Aucune de ces décisions ne réécrit la partie d’un autre joueur.

## Installation
Utiliser soit le correctif léger à la racine du projet actuel, soit le dossier Altherya_V0_8_10 de l’archive complète. Mettre le dépôt à jour, puis redéployer dans Coolify. Conserver le fichier .env et le volume /app/data. Les deux tables de campagne sont créées automatiquement au démarrage. Aucun reset du tutoriel ou des soldes n’est nécessaire.

Fermer et rouvrir l’Activity après le déploiement. Si les quotidiennes apparaissent mais pas l’onglet Aventure, la nouvelle version du frontend et de l’API n’est pas encore chargée : vérifier le redéploiement complet et rouvrir l’Activity.

Les fichiers sont préparés et testés localement ; ce téléchargement ne redéploie pas automatiquement le serveur.
