# Test du menu Banque — 13 octobre 2026

## Modification
La route Banque ouvre maintenant un composant dédié utilisant les éléments du menu bleu et or préparé et montré dans la conversation. Les textes, champs et vrais boutons sont des éléments de la structure du menu. Les panneaux sont des assets séparés ; aucune image unique avec zones de clic invisibles n'est utilisée pour la banque.

Portefeuille, Banque et Fortune affichent les données de la session du serveur. Déposer/Retirer envoient les actions existantes. Les frais sont affichés avant validation : premier retrait gratuit, puis 5 % arrondis selon le moteur existant. Validation entière, solde disponible et plafond existant de 1 milliard. Les contrôles se bloquent pendant une mutation ; aucune anticipation locale du résultat. Un rafraîchissement met les soldes à jour sans perdre le montant en cours de saisie. Fermeture, retour en ville et clavier conservés. PC : panneaux côte à côte. Mobile : contenu empilé et défilement du menu.

## Vérifications réussies
- Compilation TypeScript/Vite.
- 40 tests frontend (36 existants et 4 groupes de tests DOM du nouveau composant).
- Compilation Python API et bot ; 36 tests API.
- 3 parcours navigateur complets de la banque : 1440×900, 1186×570, 390×844. Dépôt, retrait gratuit, retrait avec frais, montant excessif bloqué, retour, rechargement et persistance des soldes dans la base locale. Aucune erreur JavaScript.
- 99 vues/parcours de régression des autres menus via browser-menu-assets.cjs. Aucune erreur JavaScript ni asset manquant.
- Inspection visuelle des captures PC et mobile ; corrections des petits fragments d'ornements voisins et de l'alignement des deux colonnes.
- Tous les fichiers API et bot sont identiques octet pour octet à la base restaurée avant cette mise à jour.
- CRC des archives complet et correctif validé.

## Limites
Tests réalisés avec le serveur local de l'Activity et une base SQLite temporaire. Aucun accès à Coolify, au Discord de production ou au PostgreSQL partagé avec Oddium ; leur fonctionnement en production reste à confirmer après le déploiement. Les captures navigateur sont uniquement utilisées pour le contrôle et ne sont pas incluses.

## Installation
Ce correctif s'applique au projet « Menus vierges interactifs » restauré (version 13, contenu identique à la version 11). Copier le contenu de son dossier Altherya_V0_8_10 dans le dossier correspondant du projet. Lancer le fichier habituel de mise à jour GitHub, puis redéployer Coolify. npm ci et npm run build sont nécessaires pour reconstruire le client ; Docker les exécute automatiquement. Aucun fichier de données ou secret n'est présent dans les archives.

En cas de doute sur la base installée, utiliser le projet complet. Ce test intègre uniquement la nouvelle banque ; les corrections annulées du contrat et des ressources ne sont pas réintroduites.

## Ajustement : fond transparent et coffre retiré
Le fond gris du composant est transparent et le coffre central est retiré du menu. Les deux panneaux gardent leur position sur PC et leur présentation empilée sur mobile. Compilation réussie ; les 3 parcours navigateur de la banque ont été rejoués avec assertions supplémentaires sur l'absence de coffre et la transparence réelle du fond. Dépôt/retrait, frais et persistance vérifiés. Capture PC inspectée. Les résultats des autres tests ci-dessus correspondent à l'intégration précédente, avant cet ajustement de présentation.
