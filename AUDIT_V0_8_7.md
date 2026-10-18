# V0.8.7 — Menu du monde

La carte originale elyndor_map.png sert directement de menu : suppression du titre et du cadre ajoutés autour de l’image, cinq zones cliquables sur les libellés de la carte et boutons d’accès adaptés au mobile. Legacy, Elarwyn, Vorak, Forge de Khaz’goram et Tour d’Ashkar sont accessibles. Les deux nouvelles destinations ouvrent leurs écrans d’entrée dans le panneau unique, avec retour au monde. Accès Forge niveau 3 et Tour niveau 5. Les régions inconnues restent sans commande.

Portée : écrans et navigation. Les combats d’Ashkar et l’atelier d’équipement de Thorgar présents dans le bot ne sont pas encore branchés à l’Activity ; l’entrée le signale et ne simule aucune récompense. Aucun changement de mécanique, d’économie ou de données partagées.

Validation : compilation TypeScript/Vite et 34 tests frontend réussis. Parcours navigateur PC/mobile étendu aux deux nouvelles destinations, à leur retour vers la carte et au chargement de l’image. Tests exécutés avec une base SQLite temporaire. Archive vérifiée par CRC ; seuls les bundles référencés dans index.html sont livrés.
