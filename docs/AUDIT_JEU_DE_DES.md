# Audit du jeu de dés

- Construction TypeScript / Vite réussie ; compilation syntaxique des 88 modules Python réussie.
- Suite interface : 136 tests réussis. Les tests couvrent les six faces, leurs opposés, chaque orientation plaçant le résultat au-dessus, les phases de déplacement et l’arrêt indépendant, la géométrie arrondie et les normales unitaires, ainsi que le silence lorsque l’audio est désactivé.
- Serveur : 19 tests ciblés réussis, dont les 36 paires de valeurs possibles des dés, les gains victoire/égalité/défaite, les mises invalides et la protection contre une même demande rejouée. Cette livraison ne modifie pas le code de production de l’API ou des moteurs : la suite complète de la version précédente n’a pas été relancée intégralement.
- Navigateur avec API réelle et base temporaire : 1440×900, 1186×570, 390×844, 320×568. Le rendu WebGL est effectivement actif pour les deux dés. Contrôle des rotations, des arrêts successifs, des valeurs finales, du portefeuille, du verrouillage des commandes et d’Échap, de la mise positive, des règles, du retour à la taverne et des limites des boutons.
- Un parcours supplémentaire vérifie le repli en CSS 3D sur mobile après refus forcé du contexte WebGL. Un parcours PC supplémentaire active le bouton audio et vérifie le déclenchement des sources de sons de contact sans erreur de navigateur.
- Inspection visuelle du lancer, du premier dé arrêté et des résultats sur PC, paysage et mobile.
- Les archives sont contrôlées par CRC ; tous les fichiers non concernés sont conservés. Les fichiers de production API et moteurs sont identiques à ceux de la version précédente.

Limites : les trajectoires sont pilotées pour afficher le résultat serveur, sans moteur physique de collisions. Le PNJ et le décor sont fixes ; les sons sont synthétiques. Les essais concernent les environnements locaux temporaires, pas le client Discord ou la base Gold/Oddium de production. Aucune modification des récompenses du tutoriel, des outils ou du système de gains.
