# Création des assets

Mode : outil intégré de génération d’images (compétence imagegen), sans API/CLI externe. Référence : modèle Pile ou face approuvé. Les PNG finaux sont intégrés dans `apps/game/public/assets/coin/`.

Prompts employés :

- pile.png : “Use case: stylized-concept. Production game texture: one circular medieval Altherya gold coin, PILE side, crowned heraldic shield with three fleurs-de-lis, engraved leaf border. Match reference coin metal and ornament. Perfect orthographic front-on flat disc centered, exactly circular, filling 92% of square canvas. No perspective, no thickness visible, no cast shadow, no text, no other objects. Real aged brass gold relief, fine beaded rim, dark recessed grooves. Transparent outside coin.”
- face.png : même spécification avec “FACE side, profile of crowned lion looking right” et conservation de l’identité de la pièce centrale de référence.
- edge.png : “Use case: stylized-concept. Game material texture for milled edge of medieval brass gold coin. Seamless rectangular strip of finely engraved vertical reeds, evenly spaced thin straight gold ridges, warm aged brass, dark narrow grooves, slight worn scratches, uniform frontal lighting, no perspective, no text, no object silhouette, fills whole landscape canvas. Designed to wrap a cylindrical coin edge. Match antique Altherya crowned lion coin.”
- table.png : “Use case: precise-object-edit. Edit target reference approved Pile ou Face tavern screen. Create clean production background preserving EXACT composition, fox host, tavern, heading PILE OU FACE, red leather pad, side PILE shield choice and FACE lion choice, all frames and lighting. Remove ONLY central large loose coin and its shadow, bottom selection diamond under FACE, all text from top Retour and Portefeuille frames, text inside central status plaque, stake amount text, all five bottom betting chips, and text/icon inside both bottom action frames. Restore natural matching leather and wood. Keep empty frames for native dynamic UI. Same landscape composition, no new elements.”

Le fond généré a également retiré les titres des plaques : ceux-ci sont restitués en texte natif centré. Les boutons et jetons réutilisent l’atlas existant `assets/blackjack/controls-atlas.png`, inclus dans le correctif. Les images de faces sont orthographiques ; l’épaisseur, l’orientation et les ombres sont produites en CSS/code.
