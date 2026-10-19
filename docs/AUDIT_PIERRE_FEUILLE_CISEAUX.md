# Audit Pierre · Feuille · Ciseaux

- Construction TypeScript / Vite réussie. Compilation syntaxique de 90 modules Python réussie.
- Interface : 143 tests réussis, dont correspondance entre noms API et trois cellules des atlas, neuf duels classiques, trois mouvements, gestes cachés avant révélation, progression de la révélation et arrêt stable.
- Serveur : 19 tests ciblés réussis (17 existants et 2 dédiés). Les neuf duels, les gains, les égalités, les mises invalides, le geste invalide et le rejeu d’une révision sont contrôlés. Le code de production API/moteurs est identique à la livraison précédente ; la suite serveur complète n’a pas été relancée.
- Navigateur avec API réelle et base temporaire : 1440×900, 1186×570, 390×844, 320×568. Vérifications : sélection, boutons +/−, mise zéro et mise excessive refusées, commandes verrouillées et Échap bloqué pendant le duel, transformation effective des mains, gestes masqués avant révélation, correspondance des deux sprites finaux avec le serveur, calcul du portefeuille, règles et focus clavier, bornes et dimensions des boutons, centrage des commandes sur mobile, retour aux jeux de la taverne.
- Sons activés sur PC : au moins trois sources de contact déclenchées. Les autres formats vérifient le réglage de réduction des animations. Pas d’erreur navigateur ni d’assets manquants sur le parcours final.
- Inspection visuelle du plateau, des gestes et des raccords de manches sur PC et mobile. Correction pendant l’audit d’une propriété de dimensions du plateau empêchant les clics, puis reprise des tests.
- Les deux ZIP sont contrôlés par CRC ; les entrées non concernées et le code de production API/moteurs restent identiques à la version précédente.

Limites : les mouvements utilisent des sprites et un fondu bref entre les trois poses, sans squelette articulé ni capture de mouvement. Décor et PNJ fixes. Sons synthétiques. Essais en local avec base temporaire, sans connexion à la base commune Gold/Oddium de production et sans déploiement Discord/Coolify. Aucun changement du système de gains, des outils ou des récompenses du tutoriel.
