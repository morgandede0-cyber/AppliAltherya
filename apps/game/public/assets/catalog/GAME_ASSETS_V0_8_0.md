# Assets des jeux V0.8.0

Images créées avec l’outil intégré de génération d’images, puis encodées en WebP en préservant l’alpha. Le menu `assets/menus/games.webp` sert de référence de style.

- `game-table.webp` : cadre de table vide, 1536 × 1024, utilisé par `game-polish.css`.
- `game-symbols.webp` : atlas 1536 × 1024, trois colonnes et deux lignes ; cerises, cloche, diamant, couronne, sept, face de dé vierge. Utilisé par `game-art.ts` ; chiffres des dés et résultats rendus dynamiquement.

## Prompt du cadre

Use case: stylized-concept. Asset type: production reusable game UI frame, not a screenshot. Reference image is style reference only: match the original medieval polished gold carved borders and sapphire blue jewels. Create a single large EMPTY ornate game table frame 1536x1024, centered, outer frame occupies x30..1506 y30..994, no text anywhere, no letters, no icons, no numbers, no game pieces. Beautiful carved golden corners and sapphire diamond gems, subtle embossed gold filigree in dark royal blue velvet/leather inside. Keep the central 85 percent spacious and dark navy almost black for readable live UI. Border thickness around 60px, elaboration confined to edges, suitable for nine-slice scaling; do not place a title plaque in the middle. Transparent background outside the frame; opaque dark blue central cloth. High-quality medieval fantasy game interface matching reference, sophisticated illuminated detail, no modern flat rectangular dashboard, no watermark, no additional floating objects.

## Prompt des symboles

Production game sprite atlas, ONE transparent image 1536x1024 precise three-column two-row regular grid, each cell512x512. Medieval fantasy realism with sumptuous metallic illuminated style, matching provided blue-and-gold medieval game reference. SIX centered separate icons, EACH within center 350x350 of its cell so generous 81px margins, no overlaps, nothing crossing cell boundaries, all objects fully visible. Top left two glossy red cherries with curved green stems; top middle a richly sculpted golden bell; top right a faceted luminous sapphire-blue diamond. Bottom left a ornate gold royal crown with sapphires; bottom middle a beautiful embossed metallic red numeral 7 with golden edges, the ONLY text is single numeral 7; bottom right a frontal ivory bone die FACE, rounded square, warm mottled bone texture and gold beveled edge, completely BLANK with NO pips, not a perspective cube. Die face must occupy same 350x350 center region, slight lit bevel depth at edges, central face flat to overlay live pips. Transparent background, no plate, no card borders, no glow beyond cell margins, no watermark or labels.
