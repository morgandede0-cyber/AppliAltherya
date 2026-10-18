# Assets des menus de quêtes

Source exacte : l’image sélectionnée par l’utilisateur, conservée dans apps/game/public/assets/quest-ui/reference.png.

Trois atlas PNG avec transparence sont fournis :
- frames.png : deux cadres vierges, soleil et boussole ; aucun texte ou montant figé.
- icons.png : épées, chope/dés, carte/boussole, Gold, étoile XP, coche verte, losange actif et losange en attente.
- components.png : bouton actif, bouton désactivé, ligne d’objectif, ligne active, séparateur et commande de repli.

Les rectangles mesurés se trouvent dans apps/game/src/ui/quest-art.json. quest-art.ts découpe les atlas par SVG sans modifier les images sources. Les textes, progressions et récompenses sont des éléments HTML vivants.

## Consignes de génération utilisées
Outil : génération d’images intégrée, édition avec l’image sélectionnée comme source, fond transparent.

Cadres : reproduire exactement les deux cadres verticaux de la source, conserver matériaux et médaillons, retirer textes, cartes, boutons et scène ; laisser les centres bleu pétrole vierges et isoler les deux cadres sur alpha.

Icônes : extraire huit objets coordonnés en grille 4×2 — épées sur bouclier, chope/dés, carte/boussole, pièces, étoile XP, coche verte, losange doré et losange sombre — sans textes et sur alpha.

Composants : reproduire les six éléments de la source en grille 2×3 — bouton bleu pétrole, variante grise, ligne vide, ligne active dorée, séparateur et commande ronde à chevron — sans textes et sur alpha.

L’illustration du livre est une découpe du visuel sélectionné. Aucun texte de l’aperçu n’est utilisé comme donnée de quête.
