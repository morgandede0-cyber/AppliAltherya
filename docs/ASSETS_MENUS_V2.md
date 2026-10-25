# Assets dédiés aux menus — 25 octobre 2026

Quatre images créées avec imagegen intégré et installées dans `apps/game/public/assets/guild/` :

| Fichier | Dimensions | Usage |
| --- | --- | --- |
| forge-scene-v2.png | 1983 × 793 | Scène du forgeron, sans éléments d’interface |
| tavern-counter-v2.png | 1983 × 793 | Comptoir et tavernier, sans titre ou panneau |
| merchant-portrait-v2.png | 1254 × 1254 | Portrait indépendant et médaillon à extérieur transparent |
| item-card-v2.png | 1536 × 1024 | Parchemin vierge à ornements intégrés et extérieur transparent |

Les deux fonds de scène sont opaques. Les deux autres PNG conservent leur canal alpha d’origine. Aucune retouche matricielle n’a été appliquée aux résultats : les images sont copiées dans le projet et dimensionnées par l’interface.

Le marchand et la taverne utilisent les personnages des références approuvées. La scène de forge remplace l’ancien recadrage. Le nouveau parchemin remplace les quatre coins rapportés sur les fiches de produits, outils, boissons, jeux et annonces. Les illustrations des jeux, les objets et les cadres déjà disponibles sont réutilisés.

Les textes, prix, noms, quantités et chapitres restent de véritables éléments interactifs ; aucun chiffre de joueur n’est inclus dans les PNG. L’entrée correspondante est ajoutée au panneau central.

Les spécifications de prompts, dimensions, formats et empreintes des fichiers sont fournis dans `ASSETS_MENUS_V2.json`. Les fichiers générés par imagegen intégré sont les originaux de production, pas des captures de navigateur.

## Installation et contrôles

Le pack d’images seules ne contient pas le code d’intégration. Pour appliquer le tout au jeu, utiliser la mise à jour cumulative Altherya_MENUS_ASSETS.zip, conserver les fichiers .env et les données, puis reconstruire et redéployer dans Coolify.

Compilation client réussie et 257 tests réussis. Parcours navigateur local sur PC et mobile : achats, ventes, forge, banque, boissons, jeux, profil, inventaire, château, tableau de bord, podium, arène et contrats. Les captures sont internes et ne sont pas livrées. Les tests ne remplacent pas un lancement sur le serveur de production dans Discord. Aucun prix, bonus ou mécanisme économique n’est modifié.
