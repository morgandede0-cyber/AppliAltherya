# Menus vierges intégrés

## Installation

Copier le contenu du dossier `Altherya_V0_8_10` dans le dépôt contenant `Dockerfile` et `apps`, envoyer les fichiers sur GitHub puis redéployer dans Coolify. La compilation du client est faite par le Dockerfile. Recharger complètement l’Activity.

Le correctif s’applique à la version « Menus alignés ». L’archive complète contient les sources et tous les assets. Les dépendances et les fichiers compilés ne sont pas inclus. Pour un essai local, exécuter `npm ci` puis `npm run build` dans `apps/game` avant de démarrer l’API.

## Présentation

Kit neuf de cinq images vierges dans `apps/game/public/assets/blank-ui`. Les textes et valeurs ne sont pas dessinés dans les images. Les boutons utilisent un véritable asset bleu/doré séparé avec un libellé HTML centré.

Les commandes existantes sont recomposées dans des cartes et des grilles. Elles conservent leurs actions serveur, validations, états désactivés et actualisations. Les petits écrans utilisent une colonne et le défilement vertical ; les bordures gardent leurs coins grâce à la découpe en neuf zones.

- Taverne, château, arène, ruelle, voleur et salle clandestine : cartes de navigation et retour au bas du menu.
- Tavernier : six boissons illustrées, sélection visible, commande et délai de service.
- Banque : soldes, dépôt et retrait dans deux zones séparées, montants et frais réels.
- Forge : choix de l’outil, comparaison actuelle/améliorée, matériaux, niveau, coût et validation.
- Marché : achat, vente et histoire séparés ; quatre emplacements par page, chapitres affichés, confirmation des transactions.
- Annonces : quatre contrats par page, contrat sur parchemin à signer, timer et récupération de récompense.
- Tableau de bord et podium : données du joueur et classement issus du serveur.
- Combat et techniques : PV, logs d’attaque, choix de technique, abandon et résultat.
- Expéditions : outil, destination, emplacements d’accessoires, récapitulatif, progression et découvertes.
- Profil et troubadour : cadres harmonisés autour des informations et du livre existants.
- Vigile et braqueur : dialogues intégrés, fenêtres de planification conservées sur clic.
- Jeux : éléments réels conservés dans le nouveau cadre, avec leurs mises, actions, résultats et animations.
- Journal et fonctions encore indisponibles : même présentation de base.

La carte d’Elyndor conserve son illustration et ses accès. Les fonctions qui ne sont pas encore reliées au moteur, notamment les défis entre joueurs et les activités de la Tour, restent indiquées comme indisponibles.

## Audit

Les contrôles de cette livraison sont détaillés dans `AUDIT_MENUS_VIERGES.md`. Les tests utilisent des bases temporaires. Le déploiement Coolify, la connexion Discord réelle et la base Gold de production ne sont pas présentés comme testés. Les fichiers de l’API et du bot sont identiques à la version de départ.
