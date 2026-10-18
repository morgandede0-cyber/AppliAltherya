# Audit du suivi des quêtes

## Changements
Ajout d’un composant TypeScript et de styles isolés par identifiant. Branchement sur la fonction de rafraîchissement du HUD afin de suivre les réponses serveur. Pagination des objectifs quotidiens, état replié mémorisé et masquage dans les menus. Les accès déclenchent les menus existants ; le suivi ne réclame pas lui-même de récompenses.

## Vérifications
Compilation TypeScript et build de production. 65 tests frontend, dont trois tests DOM du nouveau suivi : progression, pagination, repli, état tutoriel et lecture des chapitres. Compilation des modules Python de l’API et du bot. 156 tests API réussis. Essais Chromium du panneau sur PC et mobile, avec ouverture des menus et mémorisation après rechargement : 20 contrôles réussis sur 1440 × 900, 810 × 465, 390 × 844 et 320 × 568, sans erreur JavaScript.

Les fichiers de serveur et les assets sont vérifiés identiques à la base de livraison. Le nouveau module importe seulement le type Snapshot et son CSS ; aucune dépendance de production ajoutée. Le build vérifie les imports TypeScript.

## Limites
Essais locaux avec compte de test ; pas de déploiement Coolify ni de connexion Discord réelle effectués. Le moteur de campagne proposé n’est pas créé. L’économie commune Oddium n’est pas modifiée et n’a pas été validée par ces essais ; les tests API locaux ne prouvent pas une connexion à une base commune en production.
