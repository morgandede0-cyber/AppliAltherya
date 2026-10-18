# Audit de la refonte des menus vierges

## Changements vérifiés

La couche de présentation recompose les commandes des moteurs existants dans les cadres vierges. Les gestionnaires de clic, les valeurs saisies, les états désactivés et les actions serveur sont conservés. Les positions absolues des anciennes planches ne positionnent plus ces contrôles.

Le kit est commun aux lieux, avec des dispositions différentes selon la fonction : navigation, banque, comparaison d’équipement, quatre objets, quatre annonces, combat, progression et jeux. Les titres et libellés sont des textes réels. Les retours appartiennent au pied du menu. Les dialogues masquent le menu de fond et conservent leur gestion du clavier.

La banque utilise des réglages compacts avec −/+, presets 100/500/Tout et confirmations séparées. Le marché utilise quatre cartes compactes sur ordinateur ; les objets d’histoire gardent leurs chapitres. Les contrats se présentent sur parchemin. Les erreurs de braquage restent visibles dans la fenêtre de planification.

Les illustrations de boissons, d’outils, de personnages et de lieux proviennent du projet. Les nouvelles images sans textes sont dans `apps/game/public/assets/blank-ui`. Les cartes utilisent leurs surfaces vides ; les cadres sont adaptés par neuf découpes et les contrôles suivent des grilles.

## Contrôles automatisés

- Compilation TypeScript et build Vite réussis.
- 36 tests frontend réussis : modèles du commerce, pages, quantités, frais bancaires, scènes, catalogue et résultats/animations des jeux.
- Compilation des modules Python et 36 tests API réussis.
- 99 vues et parcours navigateur : ordinateur 1440 × 900, fenêtre courte 1186 × 570 et mobile 390 × 844. Achats, banque, améliorations, annonces, outils, préparation, taverne, ruelle, profil et livre. Centrage des libellés et absence de débordement horizontal vérifiés.
- 20 contrôles de jeux : cartes, roulette, rouleaux, course, barillet, dés, pièce, gestes ; résultats issus du serveur, mise invalide, erreur réseau et mouvement réduit.
- 16 contrôles de placement : plusieurs largeurs, seuil 600/601, fenêtre courte, carte complète, formulaires bancaires, matériaux, combat et techniques.
- 38 contrôles de visibilité et retour des fenêtres : une seule couche active, menu de fond masqué, fermeture et restauration.
- 10 contrôles de braquage : ouverture sur clic, combinaison, validation, reprise après erreur réseau et résultat serveur.

Les captures utilisées pour la revue sont internes. Les suites utilisent des bases temporaires et ne modifient pas les données de production. Les résultats des anciennes suites qui dépendaient du placement sur les planches ont été adaptés aux nouveaux composants ; les contrôles fonctionnels demeurent.

## Portée et limites

L’API, le bot et les moteurs économiques sont inchangés par rapport à l’archive de départ. Aucun déploiement Coolify ni essai de connexion Discord réelle ou de base Gold partagée de production n’a été effectué ici. La compilation et les tests concernent cette copie du projet.

Le lancement Windows a été ajusté pour compiler les sources avant de démarrer l’API. Sa syntaxe a été relue ; le fichier BAT n’a pas été exécuté sous Windows dans cet environnement.

Les fonctions encore indisponibles dans le moteur ne sont pas transformées en actions fictives. Les archives excluent les dépendances, le client compilé, les caches, les fichiers d’environnement et les bases de test. Leur intégrité ZIP est vérifiée avant livraison.
