# Roulette : décor et composants du modèle fourni

Référence : image-edit-target-c6ce4f0421b8ca47.png, fournie le 19 octobre 2026.

Quatre créations raster en mode édition depuis cette référence, intégrées dans apps/game/public/assets/roulette :
- scene-v2.png : conserver le casino, le croupier, les bougies, le titre et les commandes ; restaurer le tapis vert sous la roue et les cases ; vider les informations variables.
- bowl-v2.png : isoler la cuve de noyer et laiton, vue circulaire de dessus, fond transparent, sans numéros, bille ni pivot.
- rotor-v2.png : disque de noyer avec grain radial et cercles de laiton, transparent, sans numéros, bille ni axe dressé.
- spindle-v2.png : pivot doré dressé, vue depuis le joueur, détouré sur fond transparent.

Le code projette les composants circulaires dans une ellipse. Le pivot conserve son relief et reste séparé du groupe animé. Les 37 cases de la roue sont exactes, avec un seul zéro ; les numéros sont du texte natif. Le tapis vertical comporte des cases natives en perspective ; les commandes utilisent le décor et ses découpes. Le portefeuille, le statut et la mise restent dynamiques. Sur mobile, le tapis est paginé et les commandes restent dans le flux.

Le résultat est déterminé par le serveur ; la roue et la bille présentent ce résultat. Il ne s’agit pas d’une simulation physique libre. Les règles et versements existants sont conservés. Aucun changement aux prix, récompenses, autres jeux ou données des joueurs.

## Installation

Copier le contenu du dossier Altherya_V0_8_10 dans le projet existant, envoyer sur GitHub puis reconstruire et redéployer via Coolify. Le ZIP complet contient les autres jeux et corrections antérieures. Conserver les variables d’environnement et la base de données. Aucun déploiement distant n’est effectué par cette livraison.

## Vérifications

Construction TypeScript/Vite et 149 tests de l’interface réussis ; compilation syntaxique de 90 modules Python ; 5 tests serveur roulette réussis. Parcours navigateur avec API réelle et base temporaire sur PC 1440×900, fenêtre haute 806×1110 et mobile 390×844 : ajout et annulation, conservation des mises, rotation effective, verrouillage, résultat, bille finale, gains serveur, règles et retour. Inspection visuelle locale. Le client Discord de production et la base Gold/Oddium de production n’ont pas été testés.

Les fichiers de production API et moteurs sont inchangés. Les entrées non modifiées de l’archive complète sont conservées et contrôlées par CRC.
