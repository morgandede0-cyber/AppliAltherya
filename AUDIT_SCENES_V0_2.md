# Audit V0.2 — Scènes interactives

## Changements

19 décors fournis par l’utilisateur intégrés au client. Navigation depuis les enseignes du hub, points d’interaction dans les décors, portraits, retours au parent, transitions, navigation clavier par vrais boutons HTML, panneau Actions du lieu pour les petits écrans. Le cadrage conserve le ratio de chaque image et se recalcule au redimensionnement. Le jeu n’utilise plus WebGL ni les petits sprites du précédent client.

Quêtes, XP/niveaux, inventaire, achats/ventes, forge, combat avec riposte, potion, repos et sauvegarde locale conservés. Collecter un coffre ne fait plus progresser par erreur la quête du colis. Le personnage n’est sauvegardé au lancement initial qu’après sa création. Le colis et le coffre sont collectables une seule fois. Les loups peuvent être combattus à nouveau depuis le point de rencontre. Les trois minerais peuvent être renouvelés après consommation pour continuer à forger.

## Tests exécutés

13 tests Node réussis : gameplay, sauvegarde, anciens primitives/collisions plus validation des nouveaux assets, bornes des zones cliquables, cibles de navigation, accessibilité des 19 scènes depuis le hub et retours sans cycle. 4 tests Python de la passerelle réussis. TypeScript strict/Vite réussis, compilation Python réussie. Tests historiques de rendu et collisions conservés mais ils ne valident pas l’affichage du nouveau client.

Vérification d’intégrité du ZIP, puis téléchargement et comparaison de la copie enregistrée. Les PNG originaux fournis restent inchangés ; seules des copies WebP sont intégrées.

## Limites

Pas de test visuel navigateur automatisé ni d’essai Discord réel dans cet environnement. Vérification utilisateur PC/mobile nécessaire, notamment placement des zones sur les portraits et lisibilité sur téléphone. Les images sont des scènes fixes avec transitions ; pas de découpage en couches animées, de personnage librement contrôlé ou de PNJ animés. L’effet de combat et les sons sont des feedbacks simples. Certains textes des références font partie de l’image et ne sont pas des données actualisées : par exemple le panneau de quêtes du château et le récapitulatif des expéditions. Les états réels sont dans les dialogues et le journal.

Aucune connexion au Gold réel. Les scènes de champions, jeux de taverne, casino, banque, ruelle et Gazette affichent leurs limites de raccordement. Le bot original n’est pas modifié. Ceci est un essai jouable de la nouvelle navigation, pas la migration complète du bot.

## Suite

Valider ensemble le style de navigation, ajuster les zones/cadrages, puis remplacer les textes intégrés aux images par des panneaux à données réelles et raccorder progressivement les moteurs métier derrière une API authentifiée.
