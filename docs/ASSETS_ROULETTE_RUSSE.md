# Assets de la table

Images créées avec la génération d’images intégrée, à partir du modèle approuvé à barillet fermé.

- `apps/game/public/assets/russian/table.png` : décor nettoyé ; conserver perspective, cuir vert, bois, bougie, patte, livre et cadres, retirer revolver, textes variables, pastilles et jetons ; conserver le titre.
- `apps/game/public/assets/russian/gun.png` : extraire uniquement le revolver gravé au barillet fermé sur fond transparent, préserver son angle et tous ses contours. Le placement est corrigé dans le composant pour rejoindre celui de la référence.
- `apps/game/public/assets/russian/bullet.png` : cartouche ancienne en laiton et cuivre, verticale, éclairage chaud réaliste, fond transparent, sans texte ni autre objet.

Ces spécifications constituent les prompts de production. Les indicateurs dynamiques sont construits en HTML/CSS ; les jetons et boutons réutilisent l’atlas du casino. Les PNG restent des éléments visuels, les données ne sont pas gravées dans les images.
