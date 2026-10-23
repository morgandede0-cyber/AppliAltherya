# Refonte du panneau administrateur — 23 octobre 2026

Le panneau conserve les commandes existantes et les contrôles d’accès serveur. Il est organisé en sept rubriques : Vue d’ensemble, Joueurs, Royaume, Maintenance, Courrier, Transactions et Journal du personnel.

Navigation latérale sur PC, onglets horizontaux sur mobile, zone de travail dédiée et pied de fenêtre fixe. La recherche des joueurs reste basée sur le registre du tutoriel. Aucun joueur n’est sélectionné automatiquement. Le joueur choisi reste identifié pendant les opérations. Les formulaires et confirmations remplacent la fiche détaillée, avec un retour explicite à celle-ci.

Les commandes avancées sont rangées par catégories, avec recherche et pagination. La maintenance et les courriers ont leurs propres rubriques. Les valeurs de prévisualisation sont figées avant envoi ; les confirmations et protections contre les doubles opérations sont conservées. Un refus d’accès ferme le panneau et efface les vues privées. Aucun changement des autorisations serveur, de l’économie ou des récompenses.

## Validation

- Compilation de production réussie.
- 207 tests d’interface réussis.
- 57 tests serveur administrateur, commandes et courrier réussis.
- 59 contrôles navigateur réussis, aucune erreur JavaScript relevée : formats 1440×900, 1186×570, 390×844 et 320×568.
- Parcours navigateur : sélection explicite, catégories, prévisualisation et application réelle sur une base temporaire, courrier, maintenance, transactions, journal et refus non-administrateur.
- Vérification syntaxique des scripts navigateur et compilation Python réussies.

Les contrôles navigateur montent le vrai panneau avec les styles de production et une API locale réelle sur des données temporaires. Ils ne constituent pas un test de la session Discord Activity en production. Aucun déploiement ni changement de données de production n’a été réalisé.

## Installation

Cette archive cumulative contient les fichiers de code du correctif précédent, les assets PNJ déjà présents et cette refonte. Elle s’applique au projet existant ; elle ne remplace pas votre bibliothèque complète de décors. Copier le contenu de Altherya_V0_8_10 dans le dossier du projet, remplacer les fichiers et conserver les assets existants, les données et les variables d’environnement. Ajouter aussi les nouveaux fichiers, puis reconstruire et redéployer avec votre procédure habituelle.
