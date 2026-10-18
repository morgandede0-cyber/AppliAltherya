# Hub — contours discrets et enseigne de taverne

- Halo jaune peint autour de Taverne supprimé avec image_gen, à partir de l’image intégrée. Enseigne, bâtiment et disposition conservés.
- Dorures des quatre commandes du bas et du bouton Admin atténuées : cadre moins saturé et moins lumineux, texte conservé lisible.
- Survol des enseignes et personnages : trait fin et translucide, sans halo lumineux. Focus clavier maintenu.
- Nouveau nom d’image hub-predateurs-v2.png et préchargement mis à jour pour éviter l’ancienne image en cache.

## Installation

Extraire le correctif à la racine du dépôt contenant apps et Dockerfile, accepter les remplacements, envoyer tous les fichiers nouveaux et modifiés sur GitHub puis redéployer dans Coolify. Le correctif s’applique à la mise à jour précédente Hub/Ruelle interactifs. L’archive complète inclut l’ensemble du projet courant.

## Vérification

Compilation TypeScript/Vite et 105 tests frontend/DOM réussis. Contrôle du rendu, des limites d’écran, du cadre atténué et du clic Taverne sur quatre formats PC/mobile. Images et archives vérifiées. Les mécanismes, données et sauvegardes ne sont pas modifiés. Aucun déploiement distant effectué ici.
