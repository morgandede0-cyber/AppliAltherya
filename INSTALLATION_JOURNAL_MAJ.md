# Journal des mises à jour du hub

Le bouton existant « Panneau central » ouvre maintenant Le Journal d’Altherya.
Le cadre en bois, les lanternes et le fond bleu sombre sont un asset ; les dates,
titres, textes et boutons restent des éléments interactifs et accessibles.
La dernière entrée est développée, les autres se consultent au clic. Trois entrées
par page, avec flèches actives lorsqu’il existe plusieurs pages. Les commandes
Retour au hub et Échap ferment le panneau. Sur mobile, le contenu défile dans le cadre.

## Installer

Archive complète : remplacer les fichiers du projet dans GitHub puis redéployer
le service Coolify, en conservant les variables existantes et le volume de données.
Le correctif léger contient seulement cette mise à jour : extraire à la racine
DU PROJET ACTUEL (celui qui contient apps/), puis redéployer. Ne pas extraire à
l’intérieur de apps/. Aucun fichier de sauvegarde n’est fourni ni à supprimer.
Cette livraison ne modifie pas la configuration Discord ou le port du serveur.
Aucun déploiement distant n’a été effectué pendant la préparation du fichier.

## Publier les prochaines notes

Modifier `apps/game/src/ui/update-notes.ts`. Ajouter une entrée en tête de liste :
identifiant unique, date réelle ISO YYYY-MM-DD, catégorie, titre, résumé et liste
des changements effectués. Utiliser seulement des nouveautés réellement livrées.
Le nombre de pages se calcule automatiquement. Reconstruire/redéployer pour publier.
Les notes sont donc actualisables dans le projet ; il n’y a pas de formulaire
admin de publication dans cette livraison.
