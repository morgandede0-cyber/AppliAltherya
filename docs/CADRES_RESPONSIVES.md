# Contenu et cadres adaptatifs

Les menus Banque, Marchand, Forge et Tavernier répartissent maintenant la place disponible entre en-tête, contenu et commandes. Les quatre emplacements du marché restent sur la même page. La comparaison des outils, les matériaux et le coût utilisent des zones flexibles. Les commandes bancaires gardent leurs champs, raccourcis, devis et confirmations.

Les cadres d’objets et panneaux utilisent neuf morceaux de l’asset existant : les coins conservent une taille de douze pixels, les bordures et le centre s’adaptent séparément. Les dorures ne recouvrent plus les libellés. Aucune nouvelle image n’est nécessaire.

Un contrôle commun garde les fenêtres dans le viewport visible et adapte les libellés des boutons sans modifier les actions ni les champs saisis. La largeur, la hauteur, l’orientation et les changements du viewport sont pris en compte. Le hub et les positions de ses boutons restent inchangés.

Sur mobile, les trois accès du château sont présentés en cartes compactes. Le contrat des petites annonces garde son parchemin et son sablier ; les espacements et le timer sont adaptés à la place disponible. Le livre du troubadour et les contenus naturellement longs restent défilables à l’intérieur de leur zone, avec les commandes accessibles. Le mode paysage court utilise la largeur du panneau plutôt que de réduire toute l’interface par un zoom.

## Vérifications

- TypeScript et compilation Vite validés.
- 115 tests frontend/DOM : notamment repositionnement sans remplacement du champ actif et conservation des coins lors du redimensionnement.
- Contrôles navigateur ciblés : 48 contrôles Forge/Banque et 52 Marchand/Taverne sur 1440×900, 1186×570, 390×844, 320×568 ; vérification des dimensions internes des cartes et des corps de menu, des opérations et de la conservation après rechargement.
- Paysage 844×390 : 12 contrôles Forge/Banque et 13 Marchand/Taverne supplémentaires.
- Parcours général : 104 contrôles sur les quatre formats habituels, puis 26 sur mobile après adaptation du château et du parchemin.
- Navigation du hub et de la ruelle : 56 contrôles avec vérification des bornes des fenêtres, dont Profil, Monde, Arène et Panneau central.
- Aucune erreur JavaScript sur ces parcours ; inspection des captures internes représentatives.
- Compilation des 82 fichiers Python vérifiée ; modules serveur inchangés.

Les tests utilisent une base locale temporaire et le navigateur de test. Aucune connexion à la base PostgreSQL de production ou au client Discord de production. Les prix, récompenses, sauvegardes et règles économiques ne sont pas modifiés.

## Installation

Le petit correctif s’applique au projet complet récent comprenant déjà la forge et la banque. Copier ses fichiers à la racine du dépôt, envoyer sur GitHub puis reconstruire/redéployer avec Coolify. L’archive complète comprend aussi les mises à jour antérieures du hub, de la ruelle, du marchand et de la taverne.
