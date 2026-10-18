# Audit de la campagne principale

## Réalisé
Moteur de campagne dans l’API, catalogue de 32 quêtes, journal interactif et suivi Aventure à droite. Recettes de récompense uniques par joueur et quête, sauvegarde de l’objectif actif, des choix, des combats et des délais. Les Gold, XP et compteur de quêtes accomplies sont mis à jour dans la même transaction que la réception de la récompense.

Les délais utilisent l’heure serveur. Les expéditions sont contrôlées dans les voyages réellement terminés après le début de l’objectif ; les ressources sont prélevées avec une condition de stock et une transaction. Le client n’envoie jamais une somme à recevoir ni un résultat de victoire. Les réponses correctes des questions ne sont pas exposées par le snapshot. Les requêtes portent une révision de campagne ; une seconde demande identique échoue.

Le moteur de combat existant résout les rencontres de campagne dans un état séparé. Les champions, les paris, les cooldowns de l’arène et les quêtes quotidiennes ne sont pas transformés en combats d’histoire. Une victoire de campagne ne fait pas progresser un objectif intitulé combat d’arène.

## Vérifications exécutées
- Compilation Python des modules API et bot.
- Compilation TypeScript et build de production.
- 67 tests frontend réussis, dont deux nouveaux tests DOM du journal : acceptation unique en attente, progression réelle, absence de remise prématurée, niveau verrouillé et affichage des combats.
- Suite complète API : 172 tests réussis.
- Sept tests ciblés de campagne exécutés à nouveau après les derniers ajustements serveur : tutoriel et niveau, révision périmée, délais et mauvaise réponse, livraison concurrente, voyage réel, sauvegarde du combat, remise concurrente, et simulation des 32 quêtes jusqu’à la fin avec 32 reçus uniques.
- La simulation accélère les horloges et prépare des données uniquement dans les tests. Aucun bouton de saut ni endpoint de test n’existe dans le jeu livré. Ce n’est pas un parcours humain de 32 quêtes en temps réel.
- 12 contrôles navigateur du journal sur 1440 × 900, 390 × 844 et 320 × 568 : acceptation, progression du premier dialogue, délai, refus API d’une validation anticipée, limites de l’écran et reprise après rechargement.
- 23 contrôles navigateur de régression des panneaux gauche/droite sur PC et mobile. Aucune erreur JavaScript.
- Images référencées présentes ; destinations d’expédition comparées aux niveaux d’accès existants. Ressource Bois de chêne conforme au catalogue de butin.
- Conservation des assets, positions des scènes, tables de butin, texte officiel de l’histoire et moteur de combat original vérifiée à la préparation de l’archive.

## Équilibrage
Les règles empêchent de valider les trente-deux quêtes par une série de clics instantanés. Les prérequis de niveau, les voyages, les livraisons, les délais et les combats demandent une progression réelle. Le tableau joint détaille les récompenses et des simulations de combats au niveau minimum. Un ajustement après retour des joueurs demeure souhaitable : aucune simulation ne garantit l’équilibrage parfait.

## Limites et reste à faire
Essais locaux sur SQLite. Aucun déploiement Coolify ni essai OAuth Discord réel effectués. Le Gold partagé avec Oddium n’a pas été validé. Les lieux nouveaux du récit sont proposés comme des rencontres dans le journal illustré ; aucun nouvel espace librement explorable n’a été créé. Les quêtes secondaires du dossier de scénario restent à programmer.
