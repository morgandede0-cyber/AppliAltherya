# Nouvelle salle clandestine

## Installation

La mise à jour légère s’applique à la version contenant les nouveaux voleur, braqueur et vigile. Décompresser ses fichiers à la racine du projet en conservant les autres fichiers. L’archive complète contient également toutes les mises à jour précédentes.

Envoyer les fichiers sur GitHub puis redéployer dans Coolify. Pour une compilation locale, exécuter `npm ci` et `npm run build` dans apps/game. Rien n’a été déployé sur le serveur depuis cet environnement.

## Fonctionnement

La scène PC est exactement la dernière illustration validée, avec les alcôves améliorées de la roulette russe et des courses. Le mobile possède une composition verticale du même décor : les cinq jeux et le bouton Retour restent visibles sans défilement horizontal ni zoom.

Cliquer sur une table ou son enseigne ouvre le jeu existant : Blackjack, Roulette, Roulette russe, Machines à sous ou Courses de chevaux. Le bouton Retour de chaque jeu revient sur cette salle, sans ancien menu superposé. Le retour de la salle conduit à la ruelle, conformément au libellé de l’image.

Le portefeuille affiche le solde réel. Une commande discrète permet de reprendre une partie active. Les accès expirés désactivent les tables et donnent accès au vigile. Le clic vérifie également l’expiration, sans attendre le prochain rafraîchissement.

Le serveur conserve la gestion des mises, gains, limites, règles et sauvegardes. Ouvrir les jeux ne prélève aucune mise.

## Assets

- `public/assets/scenes/casino-clandestine-live.png` : image PC validée, 1672×941.
- `public/assets/casino-live/room-mobile.png` : adaptation mobile générée avec image_gen, 1024×1536.
- `public/assets/alley-live/controls.png` : atlas transparent déjà livré avec les trois personnages, réutilisé pour les informations dynamiques.

Les zones natives des boutons sont définies dans casino-room.ts pour chaque format. Le décor conserve ses textes et éléments visuels ; les boutons natifs assurent les vrais clics, le clavier et les noms accessibles.

### Génération

Outil utilisé : image_gen intégré. Image source : dernière salle validée par l’utilisateur. Prompt mobile : adaptation portrait 2:3 de la salle, même style médiéval de la ruelle, pierres anciennes, bois sculpté, or vieilli et lumières ambrées. Titre en haut ; roulette russe et hippodrome miniature dans les deux alcôves supérieures ; roulette et loup au centre ; blackjack/panthère et machine/lion au premier plan ; retour en bas. Les cinq jeux doivent rester visibles dans une pièce cohérente, avec leurs enseignes françaises uniques. L’illustration PC est conservée sans retouche supplémentaire.

## Vérifications

- Compilation TypeScript et production Vite : réussies.
- 102 tests frontend et DOM : réussis, y compris les autres menus et les trois nouveaux tests de salle.
- Navigateur : 32 vérifications réussies à 1440×900, 1186×570, 390×844 et 320×568. Les cinq jeux s’ouvrent et reviennent à la nouvelle salle ; les cibles restent dans l’écran et mesurent au moins 44 pixels ; le bon asset PC/mobile est chargé ; aucun prélèvement à la navigation ; partie réelle de machines à sous sur base temporaire avec mise et règlement vérifiés.
- Compilation des modules Python : réussie.
- Contrôle d’intégrité des ZIP et comparaison des fichiers non modifiés avec la version précédente.

Les tests utilisent une base SQLite temporaire. La connexion à PostgreSQL et au Gold partagé d’Oddium en production n’a pas été testée ici. Aucun changement de schéma, de prix, de récompense ou de logique économique n’est inclus.
