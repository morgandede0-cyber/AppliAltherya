# Six décors uniques et accès aux lieux de quête

Les six lieux de la campagne possèdent chacun un nouveau décor dédié, au format PNG 1672×941. Ils sont intégrés dans l’atlas et dans une vue de lieu en grand. Les images ne contiennent ni boutons ni données de jeu : l’accès et les actions sont des contrôles natifs.

| Lieu | Niveau minimum | Première piste | Décor |
|---|---:|---|---|
| Bureau des convois | 1 | S1-Q01 | quest-place-convois-v1.png |
| Archives de la banque | 1 | S1-Q02 | quest-place-archives-v1.png |
| Halte de la Lisière | 2 | S1-Q04 | quest-place-lisiere-v1.png |
| Atelier des sceaux | 5 | S2-Q01 | quest-place-sceaux-v1.png |
| Relais de la Pierre Fendue | 6 | S2-Q05 | quest-place-relais-v1.png |
| Belvédère des Veilleurs | 8 | S3-Q01 | quest-place-veille-v1.png |

## Déblocage

Le bouton « Entrer : [lieu] » est absent tant que les conditions ne sont pas remplies. Le serveur vérifie le niveau du lieu et l’un des critères suivants : l’étape d’exploration de ce lieu est active dans une quête acceptée ; le lieu a déjà été découvert/visité ; ou la première quête liée à ce lieu a déjà été remise. Cette dernière règle ouvre aussi les décors aux joueurs qui avaient accompli les anciennes versions de ces missions.

Un simple niveau élevé ne suffit pas à ouvrir les lieux futurs. Après ouverture, le lieu reste revisitable, sous réserve du niveau requis. L’entrée est vérifiée côté serveur, même si un client tente de forcer un bouton.

La vue du lieu affiche son décor complet, son nom et sa région. Quand la quête active y prévoit une enquête, les actions correspondantes apparaissent sous le décor. Elles consignent les indices dans le carnet. Hors de cette étape, la revisite reste contemplative avec lecture des observations déjà trouvées. Une visite ne donne ni Gold ni XP et ne rejoue pas une ancienne quête. Les récompenses de campagne gardent leurs reçus uniques et leurs montants.

Les boutons d’accès sont dans Journal → Lieux d’enquête, ainsi que sur l’objectif actif. Aucun nouveau bouton permanent n’est ajouté au hub ou à la carte du monde.

## Sauvegardes

La nouvelle table campaign_visits enregistre la première entrée de chaque joueur dans chaque lieu, avec une clé unique. Les indices restent dans campaign_evidence ; les quêtes acceptées et les récompenses déjà récupérées sont conservées. Aucun reset nécessaire. Les six images précédentes restent dans le projet pour les références historiques.

## Vérifications

- Construction TypeScript/Vite et 155 tests d’interface réussis.
- 16 tests de campagne réussis sur l’état final, dont le parcours des 32 quêtes, les droits d’entrée, les refus niveau/histoire, l’entrée obligatoire avant découverte d’indices, la persistance, les visites répétées sans récompense, les anciens reçus et la revisite après campagne terminée.
- Compilation syntaxique de 90 modules Python.
- Navigateur local avec API réelle et base temporaire : PC 1440×900 et mobile 390×844. Vérification de l’absence des accès fermés, ouverture pendant une enquête, indices, carnet, reconnexion, récompense Gold + XP puis visite en grand des six décors. Six images uniques décodées sans erreur. Vérification que l’en-tête, le titre et l’image ne se chevauchent pas ; inspection visuelle locale.
- Aucun asset manquant ni erreur navigateur sur le parcours réussi. Pas de déploiement distant ni de test sur les données Discord/Gold/Oddium de production. La suite API générale n’a pas été relancée pour cette livraison ; les tests ciblés de campagne et les tests d’interface constituent la validation automatisée.
- Archives contrôlées par CRC ; tous les fichiers non concernés sont inchangés, notamment les derniers réglages des jeux.

## Assets et prompts

Génération d’images en mode natif intégré. Chaque prompt produit un décor séparé, sans assemblage ni planche de plusieurs lieux. Chemin de destination : apps/game/public/assets/scenes/.

### Bureau des convois

Fichier : apps/game/public/assets/scenes/quest-place-convois-v1.png

Prompt final :

Use case: stylized-concept. Asset type: finished unique explorable environment for Altherya, a medieval fantasy RPG. Create ONE complete landscape scene, wide cinematic 16:9, no collage or multiple panels. Premium detailed painterly game art with realistic architecture and material textures, elegant amber lantern lighting, deep cool shadows, restrained antique brass details, coherent sophisticated medieval world, immersive eye-level view with readable foreground and depth. No UI, no borders, no menu frames, no buttons, no readable text, no numbers, no watermarks, no logos, no people, no humans, no goblins, no characters, no modern objects. Objects must remain plausible and uncluttered. Place: Bureau des convois. Interior of a medieval convoy dispatch office underneath Legacy's covered market. Open oak service counter and a clerk's desk, open bound registry with unlabelled parchment receipts, wax seal and feather pen in foreground, stacked trade crates with small recently replaced metal destination plaques, empty cobbled market visible through broad timber arch. Amber morning sunlight, burgundy and navy guild fabrics, finely worn wood, practical bustling-town atmosphere without any people. Clear foreground desk and middle-ground counter, distinctive small office, not the whole market.

### Archives de la banque

Fichier : apps/game/public/assets/scenes/quest-place-archives-v1.png

Prompt final :

Use case: stylized-concept. Asset type: finished unique explorable environment for Altherya, a medieval fantasy RPG. Create ONE complete landscape scene, wide cinematic 16:9, no collage or multiple panels. Premium detailed painterly game art with realistic architecture and material textures, elegant amber lantern lighting, deep cool shadows, restrained antique brass details, coherent sophisticated medieval world, immersive eye-level view with readable foreground and depth. No UI, no borders, no menu frames, no buttons, no readable text, no numbers, no watermarks, no logos, no people, no humans, no goblins, no characters, no modern objects. Objects must remain plausible and uncluttered. Place: Archives de la banque. A private medieval bank archive chamber in Legacy, beyond the public banking hall. Vaulted limestone ceiling, floor to ceiling oak shelves of bound ledgers and rolled mandates, low ladder, central walnut auditing desk with several large open unlabelled ledgers, wax seals and brass registration stamps. An iron grille protects the deepest aisle; small lamplight pools, warm amber brass against deep blue shadows. A quiet careful record room, not a treasure vault and no piles of coins. Wide scene with central desk visible.

### Halte de la Lisière

Fichier : apps/game/public/assets/scenes/quest-place-lisiere-v1.png

Prompt final :

Use case: stylized-concept. Asset type: finished unique explorable environment for Altherya, a medieval fantasy RPG. Create ONE complete landscape scene, wide cinematic 16:9, no collage or multiple panels. Premium detailed painterly game art with realistic architecture and material textures, elegant amber lantern lighting, deep cool shadows, restrained antique brass details, coherent sophisticated medieval world, immersive eye-level view with readable foreground and depth. No UI, no borders, no menu frames, no buttons, no readable text, no numbers, no watermarks, no logos, no people, no humans, no goblins, no characters, no modern objects. Objects must remain plausible and uncluttered. Place: Halte de la Lisière. A forgotten convoy unloading clearing at the edge of the ancient Elarwyn forest, mossy gnarled tree roots and shafts of hazy golden forest daylight. Two clear muddy wagon ruts lead from the visible woodland road to several old wooden freight crates with clean new riveted metal plaques. A low weathered stone waymarker bears only an abstract geometric carved mark. A few small brass metal shavings near one crate, rope ties intact, ferns and softly flowing stream in distance. Suspenseful but beautiful, a place to investigate, no camp tents or campfire, no characters.

### Atelier des sceaux

Fichier : apps/game/public/assets/scenes/quest-place-sceaux-v1.png

Prompt final :

Use case: stylized-concept. Asset type: finished unique explorable environment for Altherya, a medieval fantasy RPG. Create ONE complete landscape scene, wide cinematic 16:9, no collage or multiple panels. Premium detailed painterly game art with realistic architecture and material textures, elegant amber lantern lighting, deep cool shadows, restrained antique brass details, coherent sophisticated medieval world, immersive eye-level view with readable foreground and depth. No UI, no borders, no menu frames, no buttons, no readable text, no numbers, no watermarks, no logos, no people, no humans, no goblins, no characters, no modern objects. Objects must remain plausible and uncluttered. Place: Atelier des sceaux. A small craft alcove inside the mountain forge of KHAZ'GORAM, Thorgar's seal and die workshop. Carved basalt columns with restrained non-letter geometric ornament, wall rack displaying old metal stamping dies and small punches, oak-and-iron workbench with a brass die, fresh rivets, calipers and an old freight plaque, a single small brazier and low forge glow at one side, clear workshop registry without readable writing. Warm copper light, cool slate mountain daylight from a high opening. Distinct precise artisan workshop rather than a huge forge hall, no people.

### Relais de la Pierre Fendue

Fichier : apps/game/public/assets/scenes/quest-place-relais-v1.png

Prompt final :

Use case: stylized-concept. Asset type: finished unique explorable environment for Altherya, a medieval fantasy RPG. Create ONE complete landscape scene, wide cinematic 16:9, no collage or multiple panels. Premium detailed painterly game art with realistic architecture and material textures, elegant amber lantern lighting, deep cool shadows, restrained antique brass details, coherent sophisticated medieval world, immersive eye-level view with readable foreground and depth. No UI, no borders, no menu frames, no buttons, no readable text, no numbers, no watermarks, no logos, no people, no humans, no goblins, no characters, no modern objects. Objects must remain plausible and uncluttered. Place: Relais de la Pierre Fendue. An abandoned stone convoy waystation on a rugged pass of Mount Vorak. Split cliff face shelters a half-open stone building with a cracked stone arch and weathered timber roof. Interior visible naturally: old cold hearth with fresh ashes, rough wooden bench and small desk holding torn blank-map parchment fragments. Fresh boot tracks and drag marks in mountain dust lead toward a narrow lateral rocky path. Amber late-afternoon sun, wind-blown sparse grass, cool distant mountain haze. A believable safe evacuation shelter with ominous clues, no tents or people, no modern things.

### Belvédère des Veilleurs

Fichier : apps/game/public/assets/scenes/quest-place-veille-v1.png

Prompt final :

Use case: stylized-concept. Asset type: finished unique explorable environment for Altherya, a medieval fantasy RPG. Create ONE complete landscape scene, wide cinematic 16:9, no collage or multiple panels. Premium detailed painterly game art with realistic architecture and material textures, elegant amber lantern lighting, deep cool shadows, restrained antique brass details, coherent sophisticated medieval world, immersive eye-level view with readable foreground and depth. No UI, no borders, no menu frames, no buttons, no readable text, no numbers, no watermarks, no logos, no people, no humans, no goblins, no characters, no modern objects. Objects must remain plausible and uncluttered. Place: Belvédère des Veilleurs. A high observation gallery within the medieval Tour d'Ashkar, broad open carved-stone arches framing exactly three distinct mountain summits across misty forests. In the foreground an oak map table with an unlabelled parchment relief sketch, simple brass compass and north alignment marker, one warm lantern. A visible ridge path winds toward the mountains, not a river; old stone floor and restrained navy-and-gold banners with geometric emblems. Warm late-day amber light meets cool blue mist, panoramic height and contemplative mystery, no throne, no people. Distinct observation station for verifying ancient convoy maps.

## Installation

Copier le contenu du dossier Altherya_V0_8_10 du correctif dans le projet, envoyer sur GitHub puis reconstruire et redéployer dans Coolify. Le ZIP complet contient les assets et mises à jour précédents. Garder la base de données et les variables d’environnement. Aucune réinitialisation des joueurs n’est nécessaire.
