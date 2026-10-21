# Altherya — projet complet

Jeu Discord Activity : client TypeScript dans `apps/game`, serveur HTTP dans `apps/api`, moteurs de jeu et bot dans `apps/bot/tourwork`. Les moteurs du bot restent nécessaires au serveur Activity.

## Déployer sur Coolify

Placer le contenu de ce dossier à la racine du dépôt GitHub, puis reconstruire et redéployer avec le Dockerfile existant. Celui-ci compile le client et démarre l’API. Conserver les variables, le volume persistant et le port de votre installation : `PORT=10080` pour votre serveur actuel. Le défaut local du Dockerfile reste 8080 ; la variable PORT du déploiement le remplace.

Conserver `ACTIVITY_DB` sur un volume persistant et sauvegarder ce volume. Aucun fichier de données de joueur n’est livré dans l’archive. Ne pas remplacer une base de production par une base de test.

Configurer `VITE_DISCORD_CLIENT_ID` à la compilation, puis `DISCORD_CLIENT_ID` et `DISCORD_CLIENT_SECRET` côté serveur. Ne jamais inclure le secret dans le client. Conserver les autres variables de votre installation.

La version actuelle utilise la base SQLite de l’Activity. La connexion à une économie Oddium partagée n’est pas implémentée ; le serveur refuse la configuration `ECONOMY_DATABASE_URL` plutôt que de prétendre synchroniser les économies.

## Essayer localement

Avec Python et Node.js installés, lancer `DEMARRER_BRAVE.bat`. Garder sa fenêtre ouverte et ouvrir l’adresse indiquée. Le port local par défaut est 8080 ; une variable PORT déjà définie est conservée. Ne pas ouvrir directement index.html.

## Vérifier

Dans `apps/game` : `npm ci`, `npm test`, puis `npm run build`.

À la racine : `python3 -m unittest discover -s apps/api/tests -v`.

Dans `apps/bot/tourwork` : `python3 -m unittest discover -s tests -v`.

Les scripts `apps/game/tests/browser-*.cjs` couvrent les parcours dans Chromium avec Playwright et des bases temporaires. Installer les dépendances serveur et Chromium pour les exécuter. Les scripts acceptent CHROMIUM_EXECUTABLE et CHROMIUM_ARGS. Ils n’utilisent pas la base des joueurs.

## Nettoyage et audits

Voir `NETTOYAGE.md` pour le nettoyage courant et `NETTOYAGE_SUPPRESSIONS.json` pour les fichiers retirés. Les rapports AUDIT_COMPLET.md, AUDIT_ANTITRICHE.md et VERIFICATIONS_ETENDUES.md conservent les conclusions des audits précédents ; leurs nombres de tests décrivent ces versions.

Le nettoyage ne modifie ni les prix, ni le bonus du tutoriel, ni le design, ni les règles de progression. Il n’ajoute aucun reset. Les migrations déjà présentes restent inchangées. Les assets utilisés par des chemins dynamiques et les moteurs nécessaires au bot sont conservés.

## Correctif de sécurité du 21 octobre 2026

Voir AUDIT_SECURITE_20261021.md. Les sessions expirent désormais après 30 jours côté serveur ; les sessions existantes sont migrées sans reset de compte. Une nouvelle connexion Discord retrouve la sauvegarde habituelle. Les appels API sont limités pour freiner les abus ; un refus temporaire renvoie HTTP 429 avec Retry-After. Les quotas anonymes utilisent l’adresse réseau directement vue par l’application, sans faire confiance aux en-têtes transmis par le client.

Conserver votre configuration Coolify, le port 10080 et le volume ACTIVITY_DB. Reconstruire et redéployer après copie des fichiers. Aucun changement des prix, du bonus du tutoriel ou des menus.


## Panneau admin et maintenance

Voir [ADMIN_ET_MAINTENANCE.md](ADMIN_ET_MAINTENANCE.md) : commandes par catégories, recherche, aperçu/confirmation, journal, verrouillage global ou par lieu et commande Discord `/altherya-admin`. Les prix et le bonus du tutoriel sont conservés.
