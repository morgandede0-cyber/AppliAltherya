# Menus harmonisés — 25 octobre 2026

Cette mise à jour cumulative s’applique sur le projet existant. Conserver la base de données et les variables d’environnement ; reconstruire et redéployer le jeu. Aucun changement d’économie ou de sauvegarde.

## Réalisation

Une dernière couche commune `realm-theme.css` rapproche les interfaces du profil et du panneau central : vert profond, bronze ancien, texte ivoire, Georgia, champs sombres, focus visible et boutons de commande cohérents. Le nouvel asset vectoriel `assets/realm-theme/action.svg` est sans texte : les vrais libellés et états restent interactifs.

Les visuels illustrés déjà approuvés restent employés. Les zones cliquables dans les scènes et les contrôles physiques des jeux ne sont pas remplacés par de gros boutons génériques. Les contrats des annonces, le livre du troubadour, le grimoire et les chroniques gardent leurs supports spécifiques. L’inventaire reste indépendant du profil. Le tutoriel reste uniquement explicatif.

La forge dispose de marges supplémentaires pour ses matériaux, de pénuries pouvant revenir à la ligne et de boutons réorganisés sur mobile. Le fond flouté clandestin n’étend plus la largeur défilante.

## Contrôle de couverture

Le test navigateur `browser-theme.cjs` ouvre 43 états de menus sur quatre tailles : 1440×900, 1186×570, 390×844 et 320×568.

- Profil, inventaire, monde, troubadour, Khaz’goram, tour.
- Forge, boissons, annonces, château, tableau de bord, podium.
- Marchand, taverne, jeux de taverne, voleur, braqueur, vigile.
- Banque, arène, préparation d’expédition, outils, destinations, accessoires, confirmation de départ, voyage.
- Blackjack, roulette, machine à sous, roulette russe, chevaux, dés, pièce, pierre-feuille-ciseaux.
- Salle clandestine, bibliothèque de quêtes, carnet d’aventurier, port, Smogo, historique de combat.
- Courrier, comptoir entre joueurs, administration.

Ce contrôle rend les états initiaux avec un personnage de test et des réponses de service simulées pour les trois derniers menus. Il ne prétend pas parcourir toutes les combinaisons de progression ou tous les combats. Les parcours de navigation hotbarres/livres et du panneau central sont également exécutés avec une API temporaire réelle. Captures internes examinées pour le profil/inventaire, la forge et la banque.

Le script `node scripts/audit-menu-assets.mjs` contrôle les chemins littéraux dans les sources. Les tests des catalogues vérifient également les illustrations des objets et les atlas. Aucun nouvel objet ou décor manquant n’a été identifié ; les assets existants sont conservés plutôt que remplacés arbitrairement.

## Vérification locale

Depuis `apps/game` : `npm test`, `npm run build`, puis `node scripts/audit-menu-assets.mjs`. Les tests navigateur nécessitent Chromium ; `browser-theme.cjs` utilise le fichier de configuration indiqué par `HB_CHROMIUM_CONFIG` ou `/tmp/explain-chromium.json`.

Le journal des mises à jour contient cette livraison. Aucun serveur public ou salon Discord n’a été modifié automatiquement.
