# V0.8.0 — Jeux de la taverne et de la salle clandestine

## Changements

- Nouvelle table ornée avec velours bleu, or sculpté et saphirs, adaptée aux deux formats d'écran.
- Nouveaux symboles détaillés pour les rouleaux et nouvelle texture de dé en ivoire. Les points restent générés selon le résultat réel.
- Dés : mouvements en profondeur, rebonds, changement de faces pendant le lancer et arrêt sur les deux valeurs du serveur.
- Pièce : deux faces physiques, retournement en profondeur et arrêt sur la bonne face.
- Pierre-feuille-ciseaux : séquence des trois symboles avant la révélation du duel.
- Roulette : plateau des 37 numéros accessible sans ouvrir un sous-menu, choix clair et numéro sorti mis en évidence.
- Machine à sous : levier cliquable, symboles illustrés, arrêts successifs et état lumineux pendant le mouvement.
- Courses : variations de rythme et piste en mouvement ; arrivée conforme au gagnant du serveur, sans recul des chevaux.
- Roulette russe : barillet métallique animé et portrait de la hyène repris dans l'asset d'origine.
- Black Jack : dos des cartes repris dans l'asset d'origine, distribution et commandes tirer/rester conservées.
- Jetons de mise sélectionnables, commandes plus/moins, bannière victoire/défaite/mise restituée.
- Règles consultables et cinq dernières manches affichées pendant l'ouverture du jeu. Cet historique est local à l'écran courant ; ce n'est pas un historique global persistant.
- Sons de clic et de résultat uniquement lorsque le joueur a activé « Son : oui ».

Aucune modification des règles, de la distribution des résultats ou des gains côté serveur. Les animations illustrent le résultat reçu et ne déclenchent pas de mise supplémentaire. Les modes contre un ami ne sont pas ajoutés.

## Correction de livraison

Une compilation directement depuis le ZIP V0.7.9 a révélé l'absence de `apps/game/src/data/rules.ts`, référencé par les modules historiques de combat et de sauvegarde. Ce fichier est rétabli depuis le projet existant et inclus dans la livraison. Il ne remplace pas l'économie ou le moteur de jeux serveur. Les anciennes compilations ne sont pas ajoutées à l'archive : seuls les bundles référencés par la page sont conservés.

## Vérifications

- Compilation TypeScript et Vite réussie.
- 33 tests frontend réussis, dont la face finale de la pièce, les retours de mises et les trajectoires sans recul.
- 28 tests API réussis ; compilation de tous les modules Python API/bot réussie.
- Navigateur Chromium : 20 parcours sur 1440 × 1000 et 390 × 844. Huit jeux sur les deux formats, règles, jetons, plus/moins, mises invalides, animations actives, retours et manches récentes.
- Valeurs des dés, faces de la pièce, gestes, rouleaux, numéro et cheval comparés au résultat du serveur. Solde vérifié avant/après chaque manche : mise débitée une seule fois et retour réel crédité.
- Erreur réseau simulée : aucune variation du solde, commandes réactivées. Préférence de mouvement réduit : partie terminée et contrôles disponibles.
- Captures inspectées ; absence d'erreur JavaScript et de débordement horizontal après les manches.
- ZIP contrôlé et serveur démarré depuis une extraction neuve ; page, bundles et assets servis correctement. Compilation TypeScript depuis cette extraction réussie.

Base SQLite temporaire dédiée et fonds de test. Pas de déploiement, pas de test dans Brave ni dans l'Activity Discord intégrée, pas d'accès à la base Gold Oddium de production. Les tables longues restent défilables sur petit écran.

## Refaire le test navigateur

Depuis `apps/game` : installer les dépendances, compiler avec `npm run build`, installer Chromium avec `npx playwright install chromium`, puis lancer `node tests/browser-games.cjs`. Les dépendances Python de l'API doivent être installées. Le test crée sa propre base temporaire et ne modifie aucune base du projet. `SCREENSHOTS_DIR` permet de choisir le dossier des captures ; `TEST_GAME_PORT` permet de changer le port local.
