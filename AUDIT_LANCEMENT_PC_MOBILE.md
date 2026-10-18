> Rapport de la mise à jour précédente. La grille portrait et le dock paysage ont depuis été retirés : voir `AUDIT_RESTAURATION_BOUTONS.md`.

# Audit — lancement royal et affichage PC/mobile

## Changements

Écran d’attente remplacé par le modèle au blason validé. Blason PNG transparent séparé des informations ; progression, états et reprise entièrement pilotés par le code. Connexion OAuth existante conservée, avec notifications des étapes au lanceur. Aucun jeton exposé dans l’interface.

Chargement des images du hub avant son ouverture, erreurs et délais signalés, protection contre les callbacks tardifs après un échec et contre les raccourcis pendant le lancement. Pas de délai artificiel pour prolonger le chargement.

Disposition guidée par les dimensions de la fenêtre Activity, y compris sur ordinateur avec fenêtre étroite. Portrait : décor plein cadre et accès en deux colonnes ; paysage court : dock tactile ; vue large : disposition sur les bâtiments. Légère correction du chevauchement historique Annonces / Ruelle sombre. Les assets des boutons existants sont conservés.

## Validation locale

- Compilation TypeScript et build Vite de production réussis.
- 55 tests frontend réussis : régressions existantes, dimensions de fenêtre, progression et reprise après échec d’asset.
- Compilation des modules Python réussie ; 156 tests API réussis.
- Contrôles navigateur avec Chromium : lancement et hub sur 1440×900, 809×1110, 390×844, 844×390 et 320×568, rotation, limites des boutons, absence de chevauchements, cibles tactiles, navigation Banque/Profil, échec serveur et asset puis reprise : 27 contrôles réussis.
- Régressions navigateur : 15 contrôles profils/pseudos serveur/admin, 16 contrôles de placement des menus et combat, 24 contrôles de tutoriel, sauvegarde et récompense unique réussis.
- Captures examinées pour le lancement et le hub, PC et portrait ; paysage compact examiné après ajustement.
- Imports des nouveaux modules résolus par TypeScript/build ; revue ciblée des nouvelles fonctions et de leur cycle de vie. Pas de nettoyage général des anciennes fonctions inutilisées dans cette mise à jour.
- Backend, moteurs de jeu et anciens assets comparés à la base : inchangés. Aucun schéma économique modifié, aucune migration ni réinitialisation de données.
- Archive contrôlée : intégrité ZIP, présence des sources, du blason et de `apps/game/src/data/rules.ts`, reconstruction de production depuis extraction.

## Limites

Les tests navigateur sont réalisés localement avec des tailles de fenêtres PC/mobile ; ils ne remplacent pas un essai sur un téléphone physique dans Discord. La connexion OAuth réelle, les publications Discord et le déploiement Coolify n’ont pas été exécutés depuis cet environnement.

La progression affiche des jalons pondérés et les images chargées ; elle ne mesure pas les octets reçus par Discord. Les déplacements internes à une scène ne redémarrent pas le lanceur.

Le Gold reste géré par le stockage de la version Activity existante. Le partage avec Oddium n’est pas implémenté ni validé dans cette base ; cette mise à jour visuelle ne le modifie pas. La persistance après redéploiement dépend toujours du volume de données installé sur le serveur.
