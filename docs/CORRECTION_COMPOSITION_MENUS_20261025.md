# Correction des compositions de menus

La première intégration avait repris un cadre et un parchemin communs, mais pas suffisamment les compositions approuvées. Cette livraison corrige les écrans existants, avec leurs données et actions réelles.

- Marchand : portrait agrandi dans le bandeau du portefeuille, trois onglets de mode toujours visibles, rayons distincts, quatre fiches par page et un retour au pied du panneau. Les objets d’histoire conservent leurs chapitres et leur séparation.
- Forge : grande scène du forgeron au-dessus des quatre choix d’outil, comparaison illustrée avec flèche, matériaux et coût séparés. L’amélioration et le retour restent accessibles dans le pied du menu.
- Banque : comptes en médaillons et soldes dans des plaques illustrées, transfert centré et confirmation distincte.
- Taverne : bandeaux de comptoir pour les boissons et les jeux ; carte des six boissons et commande de la sélection au pied du menu ; trois grandes fiches de jeux. La navigation du décor demeure conservée.
- Profil : identité à côté du portrait, rubriques hiérarchisées et quatre outils sur PC. Les informations complémentaires restent dépliables. L’inventaire conserve uniquement son contenu et ses filtres.
- Arène : portraits dans une scène de duel, panneau de mise rectangulaire, bouton principal accessible en pied, techniques sur des cartes rectangulaires, intention, journal et résultat. Le contrôle de mise retrouve le bouton principal même après déplacement dans le DOM.
- Annonces : titres, scènes et commandes sur des zones distinctes ; contrat et timer restent séparés de la liste après signature.
- Château, tableau de bord et podium : cadre commun et conservation des composants de classement, des photos et des noms du serveur. Les trois accès du château restent réunis sur PC et passent en liste sur mobile.

Les cartes utilisent des ornements du modèle illustré et les panneaux de données un nouvel asset rectangulaire. Aucun texte ou solde n’est figé dans les images. Les prix, récompenses, recettes, conditions, contrôles serveur et règles de sauvegarde ne changent pas.

Le livre du troubadour, le grimoire, les livres de quêtes et le tutoriel conservent leur structure. Les jeux eux-mêmes gardent leurs règles et leurs animations ; cette livraison corrige les interfaces de sélection et les menus concernés.

## Vérifications

Compilation du client et de l’API, 257 tests de régression, parcours navigateur des menus sur 1440×900, 1186×570, 390×844 et 320×568, avec vérification des limites des boutons du pied de menu ; parcours hotbar et livres. L’audit des chemins littéraux relève 214 références et aucune manquante.

Les tests utilisent une base locale isolée. Les photos Discord sont simulées dans le navigateur. La base de production, le Gold partagé avec Oddium et le lancement réel dans Discord ne sont pas directement testés par cette passe. Sur les écrans courts, les données défilent à l’intérieur du panneau ; les commandes principales restent accessibles en pied. La reproduction des compositions est adaptative et n’est pas une identité pixel par pixel avec les illustrations.
