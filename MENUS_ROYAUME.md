# Menus du royaume — 18 octobre 2026

## Installation
L’archive complète contient le projet avec l’arène déjà intégrée et les nouveaux menus. L’archive légère contient uniquement les changements depuis la livraison de l’arène.

Décompressez le fichier choisi, copiez le contenu du dossier Altherya_V0_8_10 dans votre dépôt, envoyez sur GitHub et redéployez dans Coolify. Conservez vos variables privées et le stockage persistant. Aucune suppression ni remise à zéro des données n’est nécessaire. Le port reste 10080.

## Menus intégrés
- Marchand : entrée Acheter / Vendre / Histoire ; quatre emplacements par page ; histoire séparée et numéros de chapitre ; confirmation d’achat et quantités de vente.
- Forge : quatre catégories, équipement actuel et prochain palier, vrais matériaux et coût, amélioration soumise aux conditions du serveur.
- Banque : deux panneaux Portefeuille / Banque, un espace de transfert à onglets Déposer / Retirer, montants rapides et frais réels, aucune image de coffre au milieu.
- Taverne : chemins, six boissons illustrées, accès aux jeux existants, livre original du troubadour conservé avec chapitres débloqués et déblocage du prochain chapitre.
- Château : récompense quotidienne, tableau de bord personnel, podium et classement.
- Petites annonces : huit offres sur deux pages ; contrat à examiner et signer ; après signature, seul le contrat en cours et son compteur restent affichés.

Le cadre commun reprend les matériaux du panneau central et du profil. Les nombres, textes et boutons sont de vrais composants interactifs. Sur petit écran, le contenu défile à l’intérieur du cadre et les actions de retour restent en bas.

## Identité Discord
Le tableau de bord utilise le profil vérifié du joueur connecté. Le podium utilise le surnom serveur enregistré et la photo de chaque joueur classé ; il ne réutilise pas la photo du visiteur. L’API n’expose pas les identifiants Discord dans le classement. Sans photo disponible, les initiales restent visibles. La synchronisation des surnoms repose sur le bot et la configuration du serveur existants.

Cette livraison ne remplace pas l’économie SQLite actuelle par une connexion PostgreSQL/Oddium. Les règles, tarifs, récompenses et sauvegardes sont conservés.
