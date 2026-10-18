# Arène et boutons complets

## Corrections
Les titres et les cinq boutons de la ruelle utilisent les silhouettes entières du menu d’origine. Le découpage suit les contours et exclut les boutons voisins. L’échelle est calculée sur les dimensions réelles du fichier (2172×724) ; les pointes latérales et les bordures restent visibles. Le bouton de sortie affiche désormais « Quitter la ruelle », avec la même action de retour en ville.

L’arène dispose d’un panneau dédié : emblème original, rang du champion, classement, champions vaincus et portefeuille, tous issus du serveur. La préparation du combat reprend cette présentation avec une mise facultative centrée, un champ numérique, des choix rapides et les actions de départ et de retour. Les valeurs dépassant le portefeuille ou 500 Gold bloquent le départ. Un portefeuille vide ouvre le menu avec une mise nulle. Le combat existant, les techniques et les résultats sont conservés ; le duel entre amis demeure indisponible comme dans la version précédente.

Le fichier apps/game/src/data/rules.ts, absent de l’archive précédente à cause d’une exclusion trop large du nom « data », est rétabli depuis la source locale existante. Le filtre d’archivage distingue désormais les données du jeu des fichiers de base de données et des données d’exécution.

## Vérifications locales
- Compilation TypeScript/Vite et des modules Python réussie.
- 45 tests frontend et 36 tests API réussis.
- Régression générale des menus : 99 parcours PC/mobile/fenêtre basse, sans erreurs JavaScript ni assets manquants.
- Nouvelle suite arène/ruelle : 18 contrôles sur 1440×900, 1186×570 et 390×844. Silhouettes et proportions complètes, limites de la mise, portefeuille vide, choix rapide, départ réel du combat et absence de défilement dans le panneau de préparation.
- Suite de placement et combat : 16 contrôles.
- Inspection visuelle des boutons de la ruelle et des panneaux de l’arène sur PC/mobile/fenêtre basse.
- Archives contrôlées par CRC ; reconstruction du projet depuis le ZIP complet.

Les fichiers du bot, de l’API et les assets raster sont identiques à la livraison précédente. Aucun déploiement effectué ; connexion Discord et persistance du Gold partagé en production restent à vérifier sur votre serveur.
