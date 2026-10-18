# Placement des menus

## Modifications
- Marché : boutons plus mesurés, groupe centré en bas sur PC pour dégager le marchand.
- Ruelle : quatre accès répartis sur deux rangées équilibrées ; titre réduit.
- Château : tableau de bord et podium côte à côte, récompense quotidienne séparée en dessous, retour centré. L’état « Déjà récupérée » conserve sa place.
- Autres menus de navigation : groupes centrés, dernière rangée centrée même avec un nombre impair de choix, titres moins dominants.
- Contrat actif : panneau compact, titre et récompense centrés, compte à rebours sur une seule ligne, progression et actions visibles. La confirmation « Petit boulot accepté » est remplacée par l’état « Contrat signé » déjà présent ; les erreurs restent affichées.
- Adaptation aux fenêtres Discord basses et aux mobiles. Assets, actions, économie et API conservés.

## Vérification locale
Compilation TypeScript/Vite réussie ; 43 tests frontend réussis ; compilation des modules Python réussie. Suite de régression des menus : 99 vérifications PC, fenêtre basse et mobile, sans erreurs navigateur ni assets manquants. Nouvelle suite de placement : 15 parcours sur 1440×900, 1186×570 et 390×844, avec absence de chevauchement, alignements, état du daily et contrat sans défilement. Le timer a été observé en fonctionnement. Contrôle visuel des quatre menus concernés.

Le code API/bot et tous les assets sont identiques à la livraison précédente. Pas de déploiement effectué ni de contrôle de la base Gold partagée en production : ces contrôles restent à effectuer sur votre serveur.
