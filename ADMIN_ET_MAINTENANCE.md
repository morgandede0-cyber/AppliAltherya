# Administration et maintenance d’Altherya

## Accès au panneau
Dans le hub, le bouton **Admin** sur la statue reste réservé aux identifiants Discord autorisés :
- Moi : `666805849011912705`
- Panda : `342359563791761410`
- Smogo : `587578557027450900`

`ACTIVITY_ADMIN_IDS`, si défini, remplace cette liste. Aucun bouton ne permet de s’accorder ce droit. Les autorisations sont vérifiées côté serveur, y compris à la confirmation.

La navigation principale contient **Joueurs**, **Gestion du jeu**, **Maintenance**, **Journal du personnel**. Le registre conserve les joueurs Discord ayant terminé le tutoriel, avec recherche, nom du serveur et portrait. Dans la fiche choisie, **Commandes du joueur** ouvre les catégories : économie, inventaire et équipement, quêtes et histoire, combats et techniques, délais et activités, joueurs et progression. Une recherche parcourt toutes les catégories ; quatre commandes et quatre choix sont affichés par page. Le bouton Retour conserve la catégorie en cours.

## Exécuter une commande
Choisir le joueur, la catégorie et la commande. Renseigner les paramètres et un motif. **Prévisualiser** affiche la cible, les valeurs demandées et, pour les soldes et compteurs, la valeur actuelle. **Appliquer la commande** effectue la modification et l’enregistre dans le journal. L’aperçu expire après cinq minutes et appartient à son auteur. Si les données changent entretemps, il faut refaire l’aperçu. Une confirmation répétée après une coupure réseau ne rejoue pas la modification.

Les champs « Nouvelle valeur » définissent un total : pour un portefeuille de 100 et une valeur de 120, le nouveau solde est 120. Ils n’ajoutent pas 120. Une partie ou un combat doit être clôturé avant la plupart des modifications du joueur.

## Maintenance
Depuis **Maintenance**, sélectionner Tout le jeu, un lieu, un jeu ou un lieu de quête, puis Oui/Non et une durée. Zéro signifie sans limite. Le motif devient le message visible par les joueurs. Pour rouvrir, sélectionner le même périmètre et Non. Une fermeture parent s’applique aux sous-lieux : fermer la ruelle ferme ses PNJ et la salle clandestine ; fermer la taverne ferme ses jeux et le troubadour.

Les fermetures persistent après redémarrage et expirent à l’heure prévue. Les administrateurs conservent l’accès pour intervenir. Le serveur bloque les actions concernées immédiatement ; les écrans des joueurs se synchronisent à la prochaine actualisation (environ 15 secondes). La progression est conservée. Les minuteurs continuent et les données restent consultables ; les rapprochements passifs déjà dus peuvent encore s’effectuer. Cette fonction ne remplace pas un arrêt du serveur pour une opération nécessitant une base hors ligne. Aucune mise n’est automatiquement remboursée et aucune progression n’est effacée.

Le verrouillage d’un joueur est distinct : sa durée zéro déverrouille le compte. La révocation des sessions déconnecte ses appareils.

## Commandes Discord privées
Le même moteur est accessible via **/altherya-admin** : `aide`, `etat`, `maintenance`, `joueur`, `royaume`. Les réponses et confirmations sont éphémères ; chaque action vérifie les ID autorisés. La commande peut apparaître dans le sélecteur Discord sans donner accès à son exécution.

Exemples :
- `/altherya-admin maintenance lieu:global active:True motif:Intervention technique minutes:30`
- `/altherya-admin maintenance lieu:bank active:False motif:Banque réouverte minutes:0`
- `/altherya-admin joueur cible:@Joueur commande:wallet motif:Correction du solde valeur:120`
- `/altherya-admin royaume commande:announcement motif:Information joueurs texte:La tour est réouverte`

Après déploiement, le service portail de l’Activity enregistre uniquement cette commande (sans remplacer les autres commandes). Il faut son `DISCORD_BOT_TOKEN`, l’application déjà configurée, le scope `applications.commands` et, de préférence, `DISCORD_GUILD_ID` pour limiter au serveur attendu. Le bot doit être en ligne et le compte admin connecté au moins une fois à l’Activity. L’enregistrement réel et les permissions Discord restent à vérifier sur votre déploiement ; les tests locaux utilisent des simulations, sans envoyer de message sur le serveur.

## Récompenses et progression
- Repasser le tutoriel conserve la preuve de paiement : aucun second bonus.
- Repositionner une campagne conserve les reçus : une quête déjà payée peut être rejouée sans nouveau Gold ni XP.
- Revenir sur un étage déjà payé de la tour restaure la progression sans repayer cet étage.
- Annuler une expédition ne verse ni butin ni XP et ne la compte pas comme une réussite de quête. La commande « Terminer l’expédition » verse au contraire son butin prévu, une seule fois.
- Recommencer les objectifs quotidiens refuse d’effacer une journée déjà récompensée. **Autoriser un nouveau bonus quotidien** est une exception volontaire et journalisée, qui permet un nouveau paiement.
- Clôturer une partie/renoncer à un combat ne rembourse pas les mises déjà engagées.
- La distribution globale concerne uniquement les comptes Discord du registre de tutoriel, dans la base Activity.
- Gold x2 / XP x2 activent les bonus des moteurs déjà compatibles. Ils ne multiplient pas toutes les récompenses manuelles de campagne ou de contrat.

## Périmètre
Gestion des soldes, XP/niveaux, pouciels, objets et ressources, outils, armures, réputations, statistiques, progression arène/tour, techniques, chapitres, campagne, quotidiens, contrats, expéditions, délais, sessions et accès. Le classement et les tableaux de bord utilisent ces données existantes. Le panneau ne modifie pas le code, les tarifs, les contenus du scénario, les rôles Discord ou une base externe.

Le bonus du tutoriel, les prix des outils et les sauvegardes existantes ne sont pas réinitialisés par cette mise à jour. Les données restent dans la SQLite isolée de l’Activity : la synchronisation avec une économie externe n’est pas incluse.

## Installation
Sauvegarder votre base persistante, remplacer les fichiers du projet avec l’archive complète ou appliquer l’archive MAJ à la racine du projet, reconstruire et redémarrer le service. Les nouvelles tables sont créées automatiquement. Ne remplacez pas votre base ou vos variables d’environnement. Le port de production configuré reste 10080. Tester d’abord une fermeture temporaire de la banque avec un compte non-admin, puis sa réouverture.

## Catalogue des commandes

55 commandes disponibles. Les modifications de joueur ciblent un compte Discord du registre.

| Identifiant | Commande | Catégorie | Paramètres |
| --- | --- | --- | --- |
| `wallet` | Portefeuille | Économie | Nouvelle valeur (0–1000000000) |
| `bank` | Banque | Économie | Nouvelle valeur (0–1000000000) |
| `xp` | Expérience totale | Économie | Nouvelle valeur (0–1000000000) |
| `pouciel` | Pouciels | Économie | Nouvelle valeur (0–1000000000) |
| `tavern_rep` | Réputation taverne | Progression | Nouvelle valeur (0–1000000) |
| `criminal_rep` | Réputation ruelle | Progression | Nouvelle valeur (0–1000000) |
| `rating` | Classement arène | Progression | Nouvelle valeur (0–1000000) |
| `champions` | Champions vaincus | Progression | Nouvelle valeur (0–10) |
| `tower_floor` | Étages validés | Progression | Nouvelle valeur (0–10) |
| `stat_combats` | Combats | Progression | Nouvelle valeur (0–1000000000) |
| `stat_wins` | Victoires | Progression | Nouvelle valeur (0–1000000000) |
| `stat_losses` | Défaites | Progression | Nouvelle valeur (0–1000000000) |
| `stat_expeditions` | Expéditions terminées | Progression | Nouvelle valeur (0–1000000000) |
| `stat_casino_games` | Parties casino | Progression | Nouvelle valeur (0–1000000000) |
| `stat_quests_completed` | Quêtes terminées | Progression | Nouvelle valeur (0–1000000000) |
| `crime_theft_success` | Vols réussis | Progression | Nouvelle valeur (0–1000000000) |
| `crime_theft_fail` | Vols ratés | Progression | Nouvelle valeur (0–1000000000) |
| `crime_crimes_success` | Crimes réussis | Progression | Nouvelle valeur (0–1000000000) |
| `crime_heists_success` | Braquages réussis | Progression | Nouvelle valeur (0–1000000000) |
| `crime_gold_stolen` | Gold volé | Progression | Nouvelle valeur (0–1000000000) |
| `crime_biggest_loot` | Plus gros butin | Progression | Nouvelle valeur (0–1000000000) |
| `crime_caught` | Arrestations | Progression | Nouvelle valeur (0–1000000000) |
| `level` | Définir le niveau | Progression | Niveau (1–100) |
| `resource` | Définir un objet / une ressource | Inventaire | Objet (choix du catalogue), Quantité (0–1000000) |
| `tool_pickaxe` | Équiper / retirer la pioche | Équipement | Palier (0 = retirer) (0–5) |
| `tool_axe` | Équiper / retirer la hache | Équipement | Palier (0 = retirer) (0–5) |
| `tool_spear` | Équiper / retirer la lance | Équipement | Palier (0 = retirer) (0–5) |
| `tool_bag` | Équiper / retirer le sac | Équipement | Palier (0 = retirer) (0–5) |
| `armor` | Définir une armure | Équipement | Emplacement (choix du catalogue), Voie (choix du catalogue), Qualité (choix du catalogue) |
| `technique` | Accorder / retirer une technique | Techniques | Technique (choix du catalogue), Possession (0–1) |
| `loadout_clear` | Rétablir les quatre techniques de base | Techniques | Aucun |
| `story_chapter` | Ouvrir / fermer un chapitre du livre | Histoire | Chapitre (1–30), Débloqué (oui/non) |
| `campaign_position` | Repositionner la campagne (sans récompense) | Histoire | Quêtes considérées passées (0–32) |
| `campaign_stage` | Repositionner l’objectif de la quête | Histoire | Étapes considérées terminées (0–100) |
| `delay_larceny` | Libérer le délai · Petit larcin | Délais | Aucun |
| `delay_ban` | Libérer le délai · Interdiction de ruelle | Délais | Aucun |
| `delay_champion` | Libérer le délai · Champion | Délais | Aucun |
| `delay_drink` | Libérer le délai · Boissons | Délais | Aucun |
| `delay_expedition` | Libérer le délai · Terminer l’expédition et verser son butin | Délais | Aucun |
| `delay_job` | Libérer le délai · Mission en cours | Délais | Aucun |
| `delay_tower` | Libérer le délai · Quota de tour | Délais | Aucun |
| `delay_game` | Libérer le délai · Nouvelle mise | Délais | Aucun |
| `job_refresh` | Renouveler les huit annonces disponibles | Annonces | Aucun |
| `job_cancel` | Annuler le contrat sans paiement | Annonces | Aucun |
| `expedition_cancel` | Annuler l’expédition sans butin ni XP | Expéditions | Aucun |
| `round_close` | Clôturer les combats / parties sans remboursement | Combats | Aucun |
| `daily_restart` | Recommencer les objectifs quotidiens (reçus conservés) | Quêtes quotidiennes | Aucun |
| `daily_reopen` | Autoriser un nouveau bonus quotidien | Quêtes quotidiennes | Aucun |
| `tutorial_restart` | Repasser le tutoriel (sans seconde récompense) | Comptes | Aucun |
| `sessions_revoke` | Déconnecter tous les appareils | Comptes | Aucun |
| `player_lock` | Verrouiller / déverrouiller ce joueur | Comptes | Durée en minutes (0 = déverrouiller) (0–525600) |
| `maintenance` | Maintenance globale / par lieu | Royaume | Lieu (choix du catalogue), Verrouiller (oui/non), Durée en minutes (0 = sans limite) (0–525600) |
| `event` | Activer / arrêter un bonus des moteurs compatibles | Royaume | Bonus (choix du catalogue), Actif (oui/non) |
| `announcement` | Message de service (vide = retirer) | Royaume | Message (texte) |
| `gift_gold` | Distribuer du Gold aux joueurs du registre | Royaume | Gold par joueur (1–10000) |

## Clés de maintenance

| Clé | Lieu |
| --- | --- |
| `global` | Tout le jeu |
| `bank` | Banque |
| `market` | Marché |
| `forge` | Forge de Legacy |
| `khaz` | KHAZ’GORAM |
| `tavern` | Taverne |
| `tavern_games` | Jeux de taverne |
| `story` | Troubadour |
| `castle` | Château |
| `jobs` | Petites annonces |
| `arena` | Arène |
| `techniques` | Grimoire |
| `alley` | Ruelle sombre |
| `guard` | Vigile |
| `thief` | Voleur |
| `robber` | Braqueur |
| `casino` | Salle clandestine |
| `expeditions` | Expéditions |
| `elarwyn` | Forêt d’Elarwyn |
| `vorak` | Mont Vorak |
| `tower` | Tour d’Ashkar |
| `campaign` | Quêtes principales |
| `daily` | Quêtes quotidiennes |
| `world` | Monde |
| `profile` | Profil |
| `blackjack` | Blackjack |
| `roulette` | Roulette |
| `russian` | Roulette russe |
| `slots` | Machines à sous |
| `horses` | Courses de chevaux |
| `dice` | Dés |
| `coin` | Pile ou face |
| `rps` | Pierre feuille ciseaux |
| `convois` | Bureau des convois |
| `archives` | Archives de la banque |
| `lisiere` | Halte de la Lisière |
| `sceaux` | Atelier des sceaux |
| `relais` | Relais de la Pierre Fendue |
| `veille` | Belvédère des Veilleurs |

## Vérifications effectuées

386 tests serveur et 27 tests admin ciblés passent (24 tests communs, soit 389 tests distincts), ainsi que 162 tests client et 17 tests du bot. Les essais navigateur couvrent le panneau existant (38 vérifications), les nouvelles commandes et maintenances sur quatre tailles PC/mobile (56 vérifications), et les cookies en iframe HTTPS (10 vérifications). TypeScript, compilation Vite et analyse pyflakes passent. Vite conserve un avertissement de taille du bundle. Ces résultats ne garantissent pas l’absence de toute faille et ne remplacent pas un essai sur votre hébergement. Aucun envoi Discord réel, aucune réinitialisation ni modification de données de production n’ont été effectués.
