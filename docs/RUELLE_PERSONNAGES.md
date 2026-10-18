# Scènes interactives de la ruelle

Les écrans du voleur, du braqueur et du vigile utilisent les scènes sélectionnées le 18 octobre 2026, avec leurs personnages et décors. Les fonds sont vierges : les vrais boutons sont découpés dans un atlas transparent et leurs textes restent dynamiques.

## Installation

Décompresser la mise à jour à la racine du projet, en remplaçant les fichiers de même nom. Ne pas supprimer les autres fichiers. Pour le projet complet, utiliser son dossier Altherya_V0_8_10. Exécuter `npm ci` puis `npm run build` dans apps/game, ou pousser les changements sur GitHub puis redéployer dans Coolify selon la configuration existante. Cette livraison ne déploie rien sur le serveur.

## Comportement

- Voleur : larcin, choix d’une cible PNJ, crime et retour. Les délais et interdictions viennent du serveur. Le vol de joueur reste désactivé : aucune action correspondante n’existe dans l’API actuelle.
- Braqueur : seul le bouton Planifier ouvre le panneau. Commencer demande le rang déjà prévu par le jeu. Combinaison à chiffres distincts, essais et résultat sont confirmés par le serveur. Fermer conserve le braquage ; une erreur réseau conserve la saisie.
- Vigile : invitation, tarif réel ou accès VIP, entrée directe si l’accès est déjà valide. Le changement de salle attend la confirmation du serveur.
- Protection contre les doubles clics, retour clavier et focus dans les panneaux. Les décors et boutons s’adaptent au format PC/mobile.

Aucun changement des règles serveur, prix, sauvegardes, récompenses ou autres menus.

## Assets

Création avec image_gen à partir des trois scènes fournies : retrait des anciennes inscriptions et commandes en conservant personnages, pose, décor et éclairage ; création d’un atlas de composants bois/or et turquoise/or ; suppression du fond de l’atlas. Fichiers dans public/assets/scenes/alley-*-live.png et public/assets/alley-live/controls.png. L’atlas est utilisé par assetSlice, sans coordonnées de clic peintes dans les fonds.

## Validation

Compilation TypeScript/Vite, 99 tests unitaires et DOM. Test navigateur des trois scènes à 1440×900, 1186×570, 390×844 et 320×568 : ouverture directe, boutons dans l’écran, retour et panneau de braquage fermé au départ. Test du braquage sur PC et mobile : validation, échec réseau sans perte d’essai, reprise et réussite confirmée par l’API locale. Les tests utilisent une base temporaire, pas les comptes du serveur.
