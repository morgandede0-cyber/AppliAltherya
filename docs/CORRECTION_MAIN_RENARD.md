# Correction de la main du renard

Les trois poses du tavernier sont reprises pour conserver une anatomie lisible : poing fermé, paume ouverte avec quatre doigts et un pouce distinct, index et majeur levés pour Ciseaux. Les griffes longues sont remplacées par des ongles courts. Fourrure, manche, brassard, orientation et cadrage sont conservés.

Asset actif : `apps/game/public/assets/rps/fox-v2.png`. L’ancienne planche `fox.png` n’est plus chargée par ce jeu. Le nouveau nom permet de distinguer l’image corrigée dans les caches. Le préchargement et les sprites utilisent tous les deux ce nouveau fichier. Une découpe CSS du coin supérieur de la cellule retire la bande de manche de la cellule voisine sans couper les doigts. La transparence et les trois cellules de 724×724 pixels sont conservées.

## Installation

Pour une installation contenant déjà tous les jeux, copier les fichiers du correctif dans le projet, envoyer sur GitHub puis reconstruire/redéployer via Coolify. L’archive complète fournit également toutes les dépendances des huit jeux. Ne pas supprimer la base de données ni les variables d’environnement.

## Vérifications

- Construction TypeScript / Vite réussie et 143 tests interface réussis.
- Parcours navigateur avec API et base temporaires : 1440×900, 1186×570, 390×844, 320×568. Chargement explicite de fox-v2.png, sélection des gestes, mises, animation, révélation, sons optionnels, résultat serveur, portefeuille, règles/clavier, bornes des boutons et retour à la taverne.
- Inspection des trois poses dans la scène sur PC et du rendu mobile. Transparence alpha 0–255, dimensions identiques à la planche précédente, ordre Pierre / Feuille / Ciseaux.
- ZIP contrôlés par CRC et entrées non concernées conservées. Les fichiers de production API et moteurs sont inchangés ; les tests serveur n’ont pas été relancés pour cette modification d’illustration et de chemins d’images. Aucun essai sur Discord ni sur le Gold partagé de production.

## Création des assets

Mode : génération d’images intégrée, compétence imagegen, édition de l’atlas précédent avec la capture en contexte.

Prompt : “Correct the anatomy of ALL THREE fox hands. Preserve identical 3:1 horizontal atlas layout, three equal square cells, same wrist anchors, forearm angle from upper right toward lower left, scale, leather brass bracer, cream sleeve and warm tavern light. Transparent background. Replace malformed paw-like fingers with believable human-hand anatomy covered in very short fine reddish fox fur: normal palm proportions and joint structure, exactly five digits, one shorter opposable thumb and four fingers, natural knuckles, subtle short dark fingernails, no long claws. ROCK: four fingers folded into palm, single thumb crossing outside curled index/middle fingers. PAPER: exactly four long fingers and one shorter side thumb, normal lengths, middle longest and little shortest, naturally spread. SCISSORS: only index and middle extended in V; ring and little folded into palm and held by thumb. Same orientation, clothing, wrist positions and cell boundaries. No text, background or cast shadows.”
