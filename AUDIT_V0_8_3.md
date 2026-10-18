# Altherya V0.8.3 — Chapitres et nettoyage des interfaces

Chapitres des objets d’histoire fournis par le serveur à partir des exigences du récit, affichés sur les cartes et confirmations. Collection initiale : chapitre 2 ; collection suivante : chapitre 3. Quatre objets au maximum par page.

Retrait des boutons Mon personnage / Journal / Son en haut à droite. Le profil reste accessible depuis le hub et au clavier (I). Zoom et Campement retirés de la carte. Aucun changement des boutons du hub.

Rectangles plaqués sur les illustrations retirés. Les menus à informations dynamiques (banque, annonces, tableau de bord, podium, combat, techniques, destinations, accessoires, départ et suivi d’expédition) utilisent les cadres bleu et or avec des textes réels en flux ; les chiffres factices présents dans les anciennes images ne se superposent plus aux données du joueur. Sélection d’outil avec asset adapté au palier et textes sans panneau ajouté. Contrats, confirmations et résultat du combat conservés.

Validation : TypeScript et Vite ; 34 tests frontend ; 36 tests API ; compilation des modules Python ; contrôle visuel PC/mobile du marché, de la carte, des outils, de la banque et des annonces ; parcours de régression PC/mobile des menus (32 captures, aucune erreur JavaScript). Transition de la collection du chapitre 2 vers le chapitre 3 vérifiée par test API. Validation CRC et contenu de l’archive.

Limites : Brave natif, Discord réel et base Gold de production non testés. Toutes les mutations des essais utilisent des bases temporaires distinctes ; pas de modification de l’économie Oddium ni de la connexion de production.
