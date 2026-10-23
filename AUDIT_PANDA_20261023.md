# Panda à la capitainerie — 23 octobre 2026

Remplacement du maître du port par Panda, un panda massif en tenue de capitaine, avec une grosse matraque en bambou sur son bureau. La nouvelle scène remplace l’illustration existante et utilise une référence de cache renouvelée.

Les dialogues et l’interaction portent le nom de Panda. Les anciens dialogues sauvegardés sont renommés uniquement à l’affichage. Aucun indice, choix, état de combat, paiement, bonus du tutoriel ou tarif d’outil n’est réinitialisé.

## Vérifications

- Compilation Python API et bot : réussie.
- TypeScript et production Vite : réussis, avec l’avertissement existant sur la taille de certains fichiers JavaScript.
- Deux tests Panda : dialogue et progression, conservation d’une ancienne sauvegarde puis validation du dossier.
- Dix-sept tests du port réussis : parcours, verrouillage narratif, indices, choix, combats, maintenance et persistance.
- Neuf tests d’interface ciblés : port, Panda, Popie et panneau des mises à jour ; ouverture, pagination et détails du journal vérifiés.
- Douze contrôles navigateur réussis, sans erreur JavaScript, sur 1440×900, 1186×570, 390×844 et 320×568 : image chargée, bouton « Parler à Panda », dialogue, absence de paiement inattendu et limites de la fenêtre. Captures PC et mobile inspectées.

Les tests utilisent des comptes fictifs et des bases temporaires. Aucun déploiement ni accès à la base réelle des joueurs, à Coolify, au serveur Discord ou au Gold d’Oddium n’a été effectué.

Les règles du port et de Popie restent celles de la livraison précédente. La matraque est décorative.
