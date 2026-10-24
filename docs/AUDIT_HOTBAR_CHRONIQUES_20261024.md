# Vérification de la livraison

## Automatisation

- TypeScript et construction Vite : réussis.
- Compilation Python API et bot : réussie.
- 254 tests client : contrôles du HUD, progression réelle, verrouillage du tutoriel, navigation, deux volumes, pages scellées, échappement du texte, compte changé, temporisateur et clics répétés ; tests existants du journal des mises à jour et des autres menus.
- 39 tests de régression de campagne et du monde : réussis.
- 2 tests supplémentaires du sommaire serveur : contenu futur masqué et absence de mutation des soldes à la lecture.
- 33 tests de tutoriel/identité/révision : réussis ; 11 tests de sécurité des PNJ : réussis.
- 104 contrôles navigateur sur 1440×900, 1186×570, 390×844 et 320×568 : cadrage des hotbarres et du livre, ouverture des cinq fonctions, portrait, bibliothèque, deux sommaires, navigation animée, pages scellées, retour, inventaire direct, quotidiennes et fermetures. Aucune erreur JavaScript ni requête d’asset en échec.

## Contrôle visuel

Captures internes des hotbarres, des deux livres, sommaires, lecture courante et page scellée sur PC et mobile. Ajustements du papier en portrait, de la taille des libellés et des commandes de changement de page. Les textes longs défilent dans la page et les commandes restent accessibles.

## Sécurité et économie

L’interface ne crée aucune nouvelle action de récompense. Les preuves de lieu, paliers, transactions, reçus et protections existantes sont conservés. Les quêtes futures ne reçoivent aucun résumé ni objectif dans le sommaire serveur. Les textes sont ajoutés comme texte DOM. Les essais utilisent des comptes fictifs et une base temporaire.

Aucune connexion à la base de production ni à Oddium ; aucun déploiement ni message Discord réel. Une vérification après déploiement dans le client Discord reste nécessaire. Les avertissements connus de taille du bundle Vite et d’import audio demeurent non bloquants.

Archive cumulative contrôlée : intégrité ZIP, absence de doublons, présence des nouveaux visuels et conservation de la révision obligatoire du tutoriel. Les caches, dépendances, captures et données de test sont exclus.
