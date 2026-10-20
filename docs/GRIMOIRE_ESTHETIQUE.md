# Grimoire — présentation enrichie

Le livre et le parchemin validés sont conservés. Chaque technique dispose d’un bandeau sombre, d’un emblème vectoriel de son type (rapide, puissante, ultime ou garde), d’un sceau d’apprentissage et de cartouches de statistiques plus contrastés. Les techniques de la tour utilisent les accents bleus d’Ashkar. Le sommaire reprend les emblèmes et l’état appris/scellé. Le compteur de collection indique les techniques apprises, y compris les bases.

Les quatre nouveaux SVG sont des dessins vectoriels locaux : `grimoire-light.svg`, `grimoire-heavy.svg`, `grimoire-ultimate.svg`, `grimoire-defend.svg`, dans `apps/game/public/assets/ashkar/`. Aucun texte ou montant n’est figé dans les assets. Les données et commandes restent interactives.

Une brève apparition de l’encre accompagne la lecture ; elle est supprimée si la réduction des animations est activée. Les pages défilent dans le parchemin ; les commandes restent dans le livre sur PC et mobile.

Aucune modification des règles de combat, de l’économie, de l’acquisition des techniques ou des sauvegardes. La règle des boss de tour tous les dix étages reste en place. Les techniques de l’arène sont conservées.

La mise à jour s’applique au projet avec le premier grimoire (version précédente). Copier les fichiers et reconstruire normalement le client. Le projet complet intègre la même amélioration. Aucun déploiement distant réalisé.

## Vérifications

163 tests client réussis et compilation TypeScript/Vite réussie. Le parcours navigateur local utilise l’API réelle avec une base temporaire, sur PC (1440 × 900) et mobile (390 × 844) : sommaire, lecture d’une technique scellée, absence de technique à l’étage 1, victoire de Varkhaz, page de récompense, confirmation de remplacement et sauvegarde de l’Ultime. Les captures du grimoire sont inspectées ; les boutons restent dans le livre. Aucun asset requis n’est manquant dans le parcours.

Le serveur n’est pas modifié ; les données de combat, prix et règles sont celles de la version précédente. Pas de nouveau test de production Discord ou de Gold partagé Oddium.
