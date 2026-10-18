# V0.8.4 — Menus exclusifs

Un seul menu visible et utilisable à la fois. Les commandes du décor sont masquées et rendues inactives pendant un menu. Les confirmations, contrats et règles suspendent le menu parent, puis le restaurent à leur fermeture. Suppression du doublon de commandes du marché et des hotspots des scènes disposant de leur menu dédié. Nettoyage complet du panneau à la fermeture. Ouverture du profil bloquée pendant le chargement d’un lieu. Les règles des jeux ne peuvent plus être ouvertes deux fois ni interrompues par une actualisation. Le hub conserve ses boutons.

Validation : compilation TypeScript/Vite, 34 tests frontend, 36 tests API ; 38 contrôles navigateur PC/mobile sur les couches de menus ; 32 captures de régression des menus, sans erreur JavaScript. Jeux vérifiés séparément dans une base SQLite de test. Aucun déploiement ni modification de données de production.
