# Audit — reprise des modèles validés

## Écarts corrigés
Les cadres génériques et boutons en simple CSS ont été remplacés, sur les menus concernés, par des composants illustrés à découpe mesurée. Les objets du marchand ont été agrandis et le rayon de départ regroupe les quatre équipements. La forge a une comparaison en deux panneaux et une section de matériaux. La taverne a ses trois grandes scènes à arche. Le tableau d’annonces a quatre illustrations distinctes et une commande à droite. L’arène a ses anneaux, cartouches et portraits plus grands.

Le marché ouvre directement la boutique ; il ne passe plus par l’écran intermédiaire à trois cartes. La navigation Acheter / Vendre / Histoire est disponible dans la boutique ; le retour au hub est explicite.

La police retrouve un repli serif explicite sur les systèmes où Georgia n’est pas installée. Les scènes illustrées sont recadrées sans déformation. L’interface de l’arène ne défile plus automatiquement vers la mise à son ouverture sur mobile. La barre d’informations derrière le cadre est masquée pendant ces menus pour éviter son chevauchement avec les ornements.

## Contrôles
- 91 tests interface réussis ; deux contrôles ciblés de l’arène également repassés après l’ajustement de prise de focus.
- Compilation TypeScript / production réussie ; compilation Python API et bot réussie.
- 104 contrôles navigateur des services réussis, notamment ouverture directe du marché, quatre emplacements, achat réel, dépôt/retrait réels, huit annonces, signature, contrat seul, navigation de taverne, livre original et identités Discord.
- 69 contrôles navigateur de l’arène réussis : mise, combat et garde, journal, animations, victoire et versement unique, abandon, historique, acquisition et remplacement de technique, prochaine étape et phase de champion.
- 24 vérifications visuelles finales sur les cinq menus : 1440×900, 1186×570, 390×844, 320×568 ; cadre dans la fenêtre, pas de débordement horizontal, nouveaux composants chargés et absence d’erreur JavaScript.
- Revue des captures de jeu en regard des modèles approuvés ; vérification des grandes illustrations, proportions, polices, commandes et portraits. Adaptation en colonne et défilement interne sur les petits écrans.

## Conservation
L’API et tous les fichiers du bot sont identiques à la livraison précédente. Les fichiers de la banque corrigée, le lecteur/styles du livre original, ainsi que les styles de parchemin sont conservés octet pour octet. Les branches des contrats signés et à signer ne sont pas remplacées par des cartes génériques.

Prix, recettes, bonus du tutoriel, état des champions, progression et données persistantes ne sont pas remis à zéro ou rééquilibrés. Les profils de test et photos sont simulés ; aucune action n’a été envoyée au serveur Discord réel. Aucun déploiement distant ni raccordement réel à l’économie PostgreSQL/Oddium n’est effectué par cette livraison.
