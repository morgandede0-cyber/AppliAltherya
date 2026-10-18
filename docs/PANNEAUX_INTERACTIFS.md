# Panneaux indépendants : hub et ruelle

Les sept panneaux du hub, les trois panneaux de la ruelle et le retour sont de véritables boutons HTML. Les visuels originaux sont isolés par découpe SVG, à leurs coordonnées d’origine sur une scène de 1536 × 1024. Les fonds sont nettoyés séparément avec l’outil de génération intégré (suppression des panneaux et reconstruction du décor). Les atlas conservent les pixels originaux ; le masque SVG fournit la transparence à l’affichage.

Pas de double enseigne dans le fond. Survol discret, appui, clavier et réduction des animations système pris en charge. Les routes, l’autorisation Admin et les fonctions existantes sont conservées.

Validation : compilation TypeScript/Vite ; 106 tests ; contrôle navigateur des 22 clics sur panneaux PC (1440) et mobile (390), avec inspection des captures. Ce contrôle visuel isolé ne remplace pas un test de l’Activity Discord déployée. Aucune migration ou modification de l’économie.

Installation : copier le correctif dans le projet, envoyer les modifications sur GitHub et redéployer Coolify.
