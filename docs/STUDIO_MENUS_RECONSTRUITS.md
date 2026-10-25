# Menus reconstruits — 25 octobre 2026

Le composant de forge est remplacé par une vue dédiée. Les autres écrans de la refonte utilisent un nouveau moteur de composition, isolé de l’ancien habillage. Les contrôles natifs sont conservés avec leurs gestionnaires, puis placés dans des emplacements propres à chaque support vierge. Les décorations ne contiennent ni soldes, ni prix, ni noms de joueurs figés.

## Écrans

- Forge : grande scène, quatre onglets illustrés, deux grands outils, trois matériaux, conditions et coût, amélioration dans le parchemin et retour. Les préparatifs restent accessibles par le petit symbole près du titre.
- Banque : deux comptes illustrés, plaques de soldes, dépôt/retrait, montant, pas de 100, préréglages et confirmation. Les formulaires restent indépendants.
- Marchand : portrait intégré au support, modes Acheter/Vendre/Histoire, rayons, quatre objets par page, chapitres, stock, confirmation d’achat/vente et pagination. La confirmation rend le fond inactif.
- Taverne : support des six boissons et de leur commande, support distinct pour les trois jeux. Les accès du décor et le livre du troubadour sont conservés.
- Profil : photo et nom du serveur, XP, fortune, quatre équipements et réputations. Les noms d’équipements sont disponibles au survol ; les informations complémentaires et les commandes secondaires sont dans le bouton ⋯ près du titre.
- Arène : support d’accueil avec portraits et mise ; support de combat avec PV, intentions, journal, techniques et résultat. Les compteurs, recharges, confirmations et requêtes serveur restent actifs.
- Annonces, inventaire, château, tableau de bord et podium : supports de registre avec zone de contenu défilante et retour. Le contrat remplace la liste après signature. L’inventaire conserve uniquement ses objets et ses filtres.

## Assets inclus

Dix supports PNG sont installés dans `apps/game/public/assets/studio/` : forge, banque, marchand, boissons, jeux, profil, accueil d’arène, combat, registre avec commandes, registre simple. Leur extérieur transparent est conservé. Les images ont été produites par imagegen intégré à partir des références validées, puis copiées sans retouche matricielle. Le registre simple ne dessine pas de boutons inutilisés.

La police AltheryaSerif est une copie de DejaVu Serif accompagnée de sa licence. Les atlas existants d’équipements et de ressources sont également inclus dans la mise à jour afin de fournir les dépendances de la nouvelle forge. Les autres illustrations d’objets et de jeux existantes sont réutilisées.

`STUDIO_ASSETS.json` donne les dimensions, canaux alpha et empreintes des nouveaux supports. `STUDIO_PROMPTS.json` contient les prompts de production des supports. Les deux variantes particulières sont décrites ci-dessous.

- Forge : édition de la référence fournie `image(20261025-151054).png` ; reconstruction du menu portrait complet, maintien du forgeron, des quatre onglets, des deux comparaisons, des trois matériaux, du coût et des deux boutons ; suppression de tous les textes, nombres et objets dans les emplacements de données ; extérieur transparent.
- Registre simple : édition du registre commun ; suppression seulement des deux boutons utilitaires dans le parchemin, remplacement par une surface ivoire continue ; maintien du cadre, des rouleaux, du sceau et du bouton de retour ; extérieur transparent.

Les prix, bonus du tutoriel, recettes, récompenses et règles d’économie ne sont pas modifiés. Les livres de quêtes et le grimoire gardent leur fonctionnement.
