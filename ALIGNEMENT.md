# Alignement des menus — 11 octobre 2026

Cette correction part de la version « Menus recalés ». Elle conserve les menus et illustrations du projet.

## Installer sur le projet existant

1. Extraire l’archive. Copier le contenu de `Altherya_V0_8_10` dans le dépôt contenant `Dockerfile` et `apps`, en remplaçant les fichiers correspondants.
2. Envoyer les fichiers sur GitHub puis redéployer dans Coolify. Le Dockerfile compile le client.
3. Recharger complètement l’Activity après le déploiement.

Le projet complet contient les sources et tous les assets. Le correctif léger contient uniquement les fichiers modifiés et s’applique à la version « Menus recalés ». Ne pas supprimer le volume de données ni remplacer les variables d’environnement du serveur.

Pour un essai local : dans `apps/game`, exécuter `npm ci` puis `npm run build`, avant de démarrer l’API Python. Les dépendances et le client compilé ne sont pas inclus dans les archives.

## Corrections

- Libellés des boutons centrés sur la partie bleue de l’illustration, en tenant compte des marges du SVG et des proportions réellement affichées. Les longs libellés réduisent leur taille pour tenir dans le bouton.
- Zones cliquables recalées sur les illustrations, notamment à la taverne, au château et à l’arène.
- Sur mobile, les contrôles restent dans leur section d’image. Les découpes du château et de l’arène conservent leurs cadres.
- Forge : niveaux, prix et détails centrés dans leurs emplacements.
- Équipements : cadrage mesuré pour chaque type et chacun des cinq paliers, sans modifier les images sources.
- Marché : espacement des onglets et des boutons du bas corrigé ; les anciens onglets incrustés sont masqués dans les modes Histoire et Vente pour éviter les superpositions. Noms des objets limités à leur zone. Sur mobile, les onglets de vente sont présentés verticalement avec des boutons lisibles ; le bouton Histoire utilise toute sa section.
- Le redimensionnement de la fenêtre recalcule le placement des textes dans les boutons.

## Validation

Compilation TypeScript/Vite et 36 tests frontend réussis ; compilation Python et 36 tests API réussis. Revue des captures et contrôles navigateur : 99 vues de menus sur ordinateur, fenêtre courte et mobile, vérification du centre des libellés et des limites des zones cliquables ; 16 contrôles de placement et 20 contrôles de jeux et animations. La dernière adaptation des onglets du marché a ensuite été vérifiée sur quatre vues ciblées (Histoire et Vente, ordinateur et mobile).

Les essais utilisent des bases temporaires. Aucun déploiement sur Coolify ni essai avec une session Discord réelle n’a été effectué ici. Les fichiers de l’API et du bot restent identiques à ceux de l’archive de départ.
