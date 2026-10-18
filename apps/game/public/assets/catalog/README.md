# Catalogue graphique

Les textes, coûts, quantités et états sont rendus par le client ; les images ne doivent pas servir de source de données.

- `equipment.webp` : 1402 × 1122, 5 colonnes × 4 lignes. Lignes : hache, pioche, lance, sac. Colonnes : paliers 1 à 5. Rendu par `equipmentArt` dans `src/ui/catalog-art.ts`.
- `resources.webp` : 1536 × 1024, 6 colonnes × 4 lignes. Minéraux, bois, peaux et ressources diverses. Associations dans `resourceArt` ; un objet non associé garde son image de repli.
- `controls.webp` : 1536 × 1024, 4 colonnes × 4 lignes. Réserve de commandes sans texte pour les prochains écrans.
- `forge-design.webp` et `merchant-design.webp` : 1536 × 1024. Visuels approuvés utilisés pour les titres et les cadres. Les exemples de valeurs contenus dans ces images sont masqués dans le rendu interactif.

Les fichiers de jeu, cartes, dés, roue et rouleaux utilisent des SVG/DOM pour rester animables et cliquables à toutes les tailles.
