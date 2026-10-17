> Dernière mise à jour : campagne principale intégrée (32 quêtes). Lire INSTALLATION_CAMPAGNE_PRINCIPALE.md pour l’installation et CAMPAGNE_RECOMPENSES.md pour l’équilibrage. Les anciens rapports décrivent leurs livraisons respectives.

# Altherya — menus vierges interactifs

Le jeu utilise les illustrations du projet et un kit neuf de cadres et boutons vierges. Les informations, les objets, les formulaires et les actions sont de vrais éléments interactifs, reliés au moteur existant.

## Mise à jour sur Coolify

Copier le contenu de `Altherya_V0_8_10` dans le dépôt contenant `Dockerfile` et `apps`. Envoyer la mise à jour sur GitHub puis redéployer dans Coolify. Le Dockerfile compile le client. Recharger complètement l’Activity après le déploiement.

Conserver les variables d’environnement, le port configuré et le volume de données du serveur. La refonte des menus ne remplace pas cette configuration.

## Essai local dans Brave

Python et Node.js sont nécessaires. Extraire le projet, puis lancer `DEMARRER_BRAVE.bat`. Le script installe les dépendances, compile le client et lance l’API. Garder sa fenêtre ouverte et ouvrir l’adresse indiquée dans Brave.

Par défaut l’essai local utilise le port 8080 ; une variable `PORT` déjà définie est conservée. Ouvrir l’adresse du serveur, plutôt que le fichier `index.html` directement. Les archives contiennent les sources et les assets, sans dépendances ni client précompilé.

## Menus

Banque, forge, marché, taverne, boissons, annonces, château, classement, arène, techniques, ruelle, vigile, braquage et préparation des expéditions utilisent les nouveaux composants. Le profil et le livre gardent leurs informations et leur lecture dans le même cadre. La carte conserve son illustration et ses accès.

Le marché sépare les objets d’histoire et indique leur chapitre. Quatre emplacements par page ; sélection, confirmation, stock et prix issus du serveur. Les jeux gardent leurs éléments interactifs, mises, animations et résultats réels.

Les fonctions encore indisponibles restent indiquées dans le jeu. Aucun déploiement de cette archive n’a été effectué depuis cet environnement.

## Développement et contrôles

Dans `apps/game` : `npm ci`, `npm run build`, `npm test`.

Depuis la racine : installer `apps/api/requirements.txt`, puis exécuter `python -m unittest discover -s apps/api/tests -v`.

Les tests navigateur se trouvent dans `apps/game/tests`. Les suites `browser-menu-assets.cjs`, `browser-placement.cjs`, `browser-heist.cjs`, `browser-layers.cjs` et `browser-games.cjs` utilisent des bases temporaires. Elles nécessitent un client compilé et Chromium pour Playwright.

Voir `MENUS_VIERGES.md` pour l’installation et la portée des changements, `AUDIT_MENUS_VIERGES.md` pour les vérifications et `apps/game/public/assets/blank-ui/README.md` pour le kit graphique.
