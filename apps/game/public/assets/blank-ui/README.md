# Kit de menus vierges

Images originales générées pour cette refonte, sans textes, montants, objets ou personnages incrustés. Génération d’images intégrée, avec les assets du projet comme références de style.

- `frame.png` : cadre transparent réutilisable, découpé en neuf zones par `border-image` pour conserver les coins lors du redimensionnement.
- `button.png` : bouton bleu vierge ; le libellé HTML et la zone cliquable appartiennent au même bouton.
- `bank.png` : planche vierge de banque ; ses surfaces bleues servent au fond des formulaires.
- `forge.png` : planche vierge de forge ; ses surfaces en bois servent aux cartes d’équipement et de matériaux.
- `navigation.png` : planche vierge de navigation ; ses surfaces en bois servent aux cartes de navigation.

Le client compose ces éléments, les équipements, les boissons et les informations par grille et flexbox. Le contenu du jeu n’est pas une capture statique. Les montants, le stock, les niveaux, les états désactivés et les timers viennent du moteur existant.

## Consignes de génération utilisées

Cadre : métal doré médiéval, gemmes bleues, vue orthographique symétrique, centre transparent et grandes marges libres, aucun texte ni objet.
Bouton : plaque bleue horizontale, extrémités dorées symétriques, centre vide réservé au libellé, extérieur transparent.
Banque : trois plaques de solde, deux zones de transfert, deux boutons de confirmation et un retour ; toutes les zones restent vides.
Forge : quatre catégories, deux panneaux de comparaison, logements vides pour les outils, un panneau de matériaux, deux plaques de statistiques et boutons du bas ; aucun outil ou chiffre imprimé.
Navigation : trois cartes égales, logements vides pour les illustrations, descriptions et actions, puis un retour centré ; aucun personnage ou nom imprimé.

## Intégration

`menu-framework.ts` et `menu-framework.css` définissent les composants.
`blank-compose.ts` recompose les contrôles et conserve leurs événements.
Les lectures de profil et de chapitres utilisent le même cadre. Les jeux conservent leurs vrais éléments animés, leurs choix et leurs mises dans cette présentation.

Modifier les règles des composants plutôt qu’ajouter des positions indépendantes pour un écran. Les coordonnées d’échantillonnage des surfaces concernent uniquement le fond ; elles ne positionnent pas les contrôles.
