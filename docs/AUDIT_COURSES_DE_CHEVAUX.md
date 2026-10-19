# Validation des courses de chevaux

- Construction TypeScript / Vite réussie.
- 129 tests interface réussis, aucun échec.
- 235 tests serveur réussis, aucun échec ni erreur.
- Compilation syntaxique des 86 fichiers Python réussie.
- Parcours navigateur avec API réelle et base temporaire : 1440×900, 1186×570, 390×844 et 320×568. Après le dernier ajustement d’espacement, les deux formats mobiles ont été rejoués avec succès.
- Vérifications : quatre chevaux sélectionnables, refus d’une mise nulle, verrouillage pendant la course y compris Échap, progression et changements de poses, arrivée complète, classement serveur, calcul du solde, limites des boutons, absence de chevauchement entre commandes et règles sur mobile, dialogue de règles et retour à la salle.
- Tests unitaires : progression monotone, franchissement à l’heure prévue, boucle fermée, directions et phases de galop ; intégrité des rectangles et contours des 124 poses ; refus des cotes périmées avant prélèvement et protection contre une seconde demande avec la même révision.
- Inspection visuelle PC, mobile et paysage mobile. Les petits fragments des poses voisines ont été exclus par des contours de rendu individuels ; les PNG originaux restent intacts.

L’animation est un rendu 2D par poses avec perspective et profondeur, sans moteur physique 3D. Le résultat et les gains restent déterminés par le serveur ; les probabilités et coefficients existants sont conservés. La scène du renard reste fixe. Aucun essai sur la base de production ni dans le client Discord de production. Aucun changement des bonus du tutoriel, des prix des outils ou des autres menus.
