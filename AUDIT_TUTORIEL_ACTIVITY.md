# Tutoriel de début réintégré dans l’Activity

## Source et parcours
Le tutoriel existant est présent dans apps/bot/tourwork/main.py : TutorialIntroView, TutorialNavigationView, TutorialProfileView, TutorialStartView, TutorialPlacesView et TutorialRewardView. Ses constantes sont définies dans tutorial_engine.py : 100 Gold et 25 XP. Cette livraison restaure sa version Activity : accueil par le garde, repérage, personnage, bien démarrer, lieux et dernière étape de bienvenue.

Le nom de la cité est adapté à Legacy et les textes décrivent les fonctions effectivement disponibles dans l’Activity. Les mentions du Pouciel et des contenus encore incomplets ne sont pas présentées comme des fonctionnalités disponibles. Il s’agit du guide de démarrage du jeu ; l’inscription du serveur Discord (langue, pseudo, règlement, rôles) reste un système séparé.

## Fonctionnement
- Ouverture après le choix du nom, ou au démarrage d’un profil dont le tutoriel n’est pas terminé.
- Étape conservée côté serveur, reprise au rechargement, bouton de navigation toujours visible ; le texte du panneau défile sur les petits écrans.
- Relecture depuis Mon profil → Refaire le tutoriel. Le bouton reste présent dans les onglets du profil et après ses rafraîchissements.
- Récompense unique, calculée par le serveur et jamais par le client. Gold, XP, niveau et marqueurs sont écrits dans la même transaction SQLite. Les requêtes concurrentes n’avancent pas plusieurs étapes et ne doublent pas les gains. Une erreur annule entièrement la transaction.
- Les drapeaux existants de tutorial_progress sont conservés ; une relecture ne les réinitialise pas. Les autres activités et le design validé de l’arène sont conservés.
- Le tutoriel du bot et ses assets ne sont pas modifiés. Une proposition graphique en image est produite séparément : elle n’est pas intégrée dans cette archive, dont les écrans restent composés avec les assets interactifs existants.

## Vérification locale
Compilation TypeScript/Vite et modules Python réussie. 45 tests frontend et 51 tests API, dont 15 tests de progression, reprise après redémarrage, contrôle des étapes, relecture, isolation des profils, concurrence et annulation de transaction.

123 contrôles navigateur dans cette livraison : 24 pour le tutoriel (six écrans, reprise, erreur réseau/retry, hub après sortie, dépôt bancaire et relecture sans gains), 99 pour les menus/assets (les contrôles jeux et placements de la livraison précédente restent décrits dans son audit). Formats : PC, fenêtre Discord basse, mobile. Contrôle visuel du texte, des panneaux et de la navigation ; contrôle du ZIP et reconstruction après extraction.

## Limites et production
Les essais utilisent l’adaptateur Activity existant et une base SQLite temporaire. En configuration Discord (DISCORD_CLIENT_ID et DISCORD_CLIENT_SECRET présents), l’identité est vérifiée par OAuth avant d’ouvrir le tutoriel. La table activity_discord_accounts rattache plusieurs sessions au même profil. Le serveur refuse les actions de jeu avant validation complète du tutoriel ; aucun contournement par appel direct à l’API n’est autorisé.

La liste privée activity_tutorial_receipts conserve l’identifiant Discord, le nom, la date et les montants validés. Sa clé unique discord:<identifiant> interdit un second versement. La remise des récompenses et les marqueurs sont enregistrés dans une même transaction. Changer de navigateur, supprimer ses cookies ou redémarrer le serveur ne crée pas une nouvelle récompense pour ce compte Discord. Le nom reste celui du personnage ; aucune liste publique ni interface admin n’est ajoutée.

Les profils locaux déjà terminés sont conservés. Les sessions anciennes sont migrées sans supprimer leurs jetons. Pour des doublons Discord historiques, le rattachement privilégie le profil déjà récompensé ; les anciens soldes ne sont ni fusionnés ni supprimés et les versements historiques ne sont pas annulés. En mode local sans configuration OAuth, le tutoriel reste utilisable pour les tests mais son identité est celle du profil local, pas celle d’un compte Discord vérifié.

Cette mise à jour n’ajoute pas de connexion à l’économie PostgreSQL/Oddium : l’adaptateur existant refuse toujours ECONOMY_DATABASE_URL. Le helper Gold global du bot n’est pas invoqué dans l’Activity. Les simulations OAuth utilisent une réponse de test contrôlée ; aucun vrai compte Discord ni serveur Coolify n’a été testé.

Les annonces publiques de fin de tutoriel du bot ne sont pas déclenchées par cette livraison. Aucun déploiement ni contrôle Discord, Coolify ou Gold partagé en production n’a été effectué. Conservez la base ACTIVITY_DB sur votre volume persistant pour garder la progression et les marqueurs après redéploiement. Aucun menu admin n’a été ajouté.
