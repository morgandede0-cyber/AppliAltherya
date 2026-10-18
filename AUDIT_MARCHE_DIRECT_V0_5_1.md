# Correctif V0.5.1 — Marché direct

Les quatre boutons Histoire, Acheter, Vendre et Partir sont intégrés à la scène du Marché. Le panneau intermédiaire et sa deuxième illustration sont supprimés du code et du CSS. Retour au marchand ferme la boutique et retrouve cette scène. Partir retourne au hub. Les quatre objets par page et la séparation Histoire sont conservés.

Disposition PC : boutons sur la partie basse du décor, sans couvrir le visage du marchand. Mobile portrait : mêmes boutons sous le décor, dans la même scène, sans fenêtre supplémentaire. Les zones cliquables correspondent aux images des boutons. Aucun ajout à l’économie ou à la base de données.

Compilation TypeScript/Vite réussie. 23 tests TypeScript et 14 tests Python passent, dont le contrôle des quatre boutons/actions directement définis dans la scène. Les limites de l’audit V0.5 restent applicables : aucun contrôle visuel Brave ou mobile possible dans cet environnement, pas de branchement sur l’économie Discord/Oddium, aucune mise en production.
