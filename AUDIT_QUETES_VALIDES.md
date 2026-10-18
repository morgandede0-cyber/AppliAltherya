# Audit — menus de quêtes validés

## Réalisé
Deux panneaux latéraux sont intégrés à partir de l’image sélectionnée. Les cadres, icônes et commandes proviennent de trois atlas illustrés transparents. Les textes, étapes, compteurs, gains et états des boutons sont calculés à partir des données actuelles du serveur.

La récupération quotidienne appelle l’action quests_claim existante. Elle est bloquée avant accomplissement, pendant l’envoi et après attribution. La navigation vers la campagne, les chroniques, les missions et les objectifs reste disponible. L’historique réel et les récompenses de campagne ne sont pas remplacés par les exemples de l’aperçu.

## Vérifications réussies
- Compilation TypeScript et production Vite.
- Compilation Python API et modules du bot.
- 95 tests d’interface, exécutés dans 24 fichiers avec vérification de chaque sortie : compteurs, pagination, repli, tutoriel masqué, navigation, verrouillage de récupération, erreur récupérable et absence de duplication des éléments visuels au fil des actualisations.
- 221 tests API.
- 23 contrôles navigateur du suivi et de sa navigation sur PC et mobile.
- 56 contrôles navigateur des nouveaux assets et de la récupération quotidienne : trois objectifs terminés, une seule requête malgré double clic, versement du montant serveur, état déjà récupéré après rechargement, états des étapes de campagne et navigation vers les détails.
- 104 contrôles navigateur de régression des services : marché, forge, banque, taverne, jeux, livre original, contrats et château.
- Dimensions contrôlées : 1440×900, 1186×570, 810×465, 390×844 et 320×568 selon les suites. Aucune erreur JavaScript relevée. Captures inspectées ; correction de la priorité des styles, des commandes de repli et des proportions des médaillons.

## Conservation et limites
L’API et tous les modules du bot restent identiques octet pour octet à la version de départ. Les écrans du château de la livraison précédente, la banque, le livre du troubadour et le parchemin des contrats sont conservés. Aucun changement de prix, de récompense, de tirage quotidien, de conditions de déblocage ou de sauvegarde. Aucun reset de progression.

Les contrôles utilisent des bases SQLite temporaires et des identités/photos de test. Aucun déploiement distant ni vérification réelle de la base PostgreSQL/Oddium ou du serveur Discord n’est effectué dans cette livraison.
