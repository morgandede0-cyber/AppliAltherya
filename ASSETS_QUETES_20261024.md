# Assets des quêtes — 24 octobre 2026

Six images originales ont été générées individuellement avec l’outil intégré de génération d’images, en demandant un arrière-plan transparent. Les PNG RGBA originaux ont été copiés dans le projet sans modification de leurs pixels ni de leur canal alpha.

| Asset | Fichier dans le projet | Utilisation |
| --- | --- | --- |
| Reçu suspect | apps/game/public/assets/quest-world/v1/recu.png | Double du contrat au Bureau des convois ; sac de quête |
| Attestation bancaire | apps/game/public/assets/quest-world/v1/attestation.png | Document remis par la banque ; sac de quête |
| Plaque de transport | apps/game/public/assets/quest-world/v1/plaque.png | Plaque à récupérer sur la caisse à la Lisière ; sac de quête |
| Fragments du journal | apps/game/public/assets/quest-world/v1/journal.png | Découverte au relais de Vorak ; sac de quête |
| Balise de piste | apps/game/public/assets/quest-world/v1/balise.png | Vérification des balises et balisage du retour dans les missions concernées |
| Étais de secours | apps/game/public/assets/quest-world/v1/etais.png | Consolidation du passage dans « Les hommes sous la pierre » |

Les documents récupérés disparaissent du point d’enquête et sont remplacés par la marque de découverte. Leurs illustrations restent consultables dans le sac de quête, avec l’état de remise au destinataire. La plaque conserve sa collecte directe dans le décor. Les balises et les étais validés restent visibles comme éléments installés, avec une petite marque de validation.

Le chargement des fichiers utilise une liste fixe d’identifiants. Aucun nom d’objet ou identifiant reçu n’est utilisé pour composer librement une URL d’image. Les illustrations ne créent ni nouvel objet commercial ni récompense et ne modifient pas la progression serveur.

## Contrôles

- Six PNG RGBA avec des pixels totalement transparents et des silhouettes détaillées. Dimensions, canal alpha et empreintes SHA-256 dans ASSETS_QUETES_CONTROLE_20261024.json.
- Prompts complets et méthode dans ASSETS_QUETES_GENERATION_20261024.json.
- Compilation TypeScript / Vite réussie ; avertissement préexistant sur la taille du bundle.
- 217 tests d’interface réussis, dont contrôle des chemins d’assets, identifiants non reconnus, interactions de quête et journal des mises à jour.
- 52 contrôles navigateur sur le jeu compilé et une API locale réelle, en 1440×900 et 390×844 : reçu dans la scène, disparition après découverte, visuel dans le carnet, collecte de la plaque, étais et balises. Aucune erreur JavaScript relevée.
- Tous les fichiers serveur sont identiques à la précédente livraison. Les suites serveur de cette précédente livraison ne sont pas présentées comme de nouveaux tests pour cette mise à jour visuelle.

Les contrôles navigateur emploient des joueurs et une base temporaires. Aucun déploiement Discord Activity ni changement de données sur votre serveur de production.

## Installation

Archive cumulative à appliquer au projet existant. Copier le contenu de Altherya_V0_8_10 dans votre projet, accepter les remplacements et ajouter les nouveaux fichiers, notamment le dossier apps/game/public/assets/quest-world/v1. Conserver les décors et assets déjà installés, les données et les variables d’environnement. Reconstruire puis redéployer avec votre procédure habituelle.
