# Assets de la reprise des modèles

Mode : génération d’images intégrée à partir des références approuvées, puis assemblage dans les composants HTML/SVG du projet. Aucune capture de menu avec des valeurs figées n’est utilisée comme interface.

Fichiers finaux dans apps/game/public/assets/faithful/ :
- ornaments.png : atlas 4 × 2 (1774 × 887), boutons bleu pétrole et bronze, carte rectangulaire, carte à arche, anneau de portrait, séparateur, deux flèches rondes.
- tavern-scenes.png : atlas de trois scènes de taverne (1536 × 1024).
- job-scenes.png : atlas de quatre illustrations de missions (1254 × 1254).
- tavern-frame.png : cadre vierge de la taverne (1536 × 1024, alpha conservé).
- jobs-frame.png : cadre vierge des annonces (1536 × 1024, alpha conservé).

Les fenêtres des ornements sont mesurées dans src/ui/approved-art.json. Le rendu coupe les cellules par SVG et garde les images sources intactes. Les scènes gardent leurs proportions ; elles ne sont pas étirées pour remplir les cartes. Les boutons restent des éléments accessibles, avec leurs actions et états verrouillés.

## Prompts finaux

1. Ornements, références marchand/forge/taverne/annonces/arène : créer un atlas de production 4 colonnes × 2 rangées, huit cellules égales sur fond transparent, sans texte, reprenant les ornements métalliques sculptés des modèles. Ligne 1 : bouton bleu pétrole vide à doubles bords dorés biseautés ; même bouton bronze actif ; carte vide rectangulaire bleu pétrole, double filet et coins ouvragés ; carte vide haute à sommet arqué, écusson et zone basse. Ligne 2 : anneau de portrait circulaire vide avec quatre losanges de boussole ; séparateur horizontal à fleur centrale ; flèche précédente ronde bronze ; même flèche suivante. Ni objets, ni personnages, ni chiffres dans les composants.

2. Scènes de taverne, référence du menu validé : atlas de trois scènes verticales, sans interface ni texte. À gauche, grande chope de bière mousseuse sur comptoir avec tavernier flou derrière ; au centre, dés sortant d’un gobelet en cuir et cartes sur table ; à droite, luth, livre illustré et bougie. Peinture médiévale réaliste, lumière ambre et ombres bleu pétrole. Reprendre les scènes approuvées plutôt que proposer un nouvel univers.

3. Annonces, référence du tableau validé : quatre cellules indépendantes sur atlas 2 × 2. Caisses et corde dans une rue médiévale ; lettre scellée, encrier et plume ; charrette marchande chargée ; lanterne et colis au crépuscule. Sujet à gauche et ombre bleu pétrole à droite pour la transition vers les textes. Aucun texte, cadre ou bouton.

4. Cadre taverne, édition de la référence : garder le cadre extérieur exact, bois sombre, coins dorés sculptés, boussole, bannières courtes et lanternes. Enlever titre, cartes, images, commandes et légendes ; remplir l’intérieur de matière bleu pétrole vierge. Supprimer le décor extérieur en transparence, sans couper le cadre. Aucune inscription ni donnée.

5. Cadre annonces, édition de la référence : garder le cadre fin en bois sombre, coins ouvragés, boussole centrale, petites bannières et lanternes. Retirer tous les contenus, cartes, pagination et inscriptions ; intérieur bleu pétrole vierge avec motif de boussole ; extérieur transparent. Préserver la composition du modèle.
