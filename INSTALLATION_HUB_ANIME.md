# Hub animé — image et boutons conservés

Cette mise à jour ajoute des effets discrets sur le hub existant : variations de lumière des lanternes et de la forge, fumée au-dessus de la cheminée, gouttelettes et reflets dans la fontaine.

L’image d’origine est conservée octet pour octet. Les bâtiments, personnages, menus et boutons restent à leur place. Il ne s’agit pas de la démo 2,5D : aucun déplacement du joueur ni nouvelle disposition n’est ajouté.

## Installation

Projet complet : décompresser et remplacer le contenu du dépôt par celui du dossier `Altherya_V0_8_10`, puis reconstruire et redéployer dans Coolify.

Correctif léger : copier son contenu sur la version « Boutons d’origine », puis reconstruire et redéployer. Ne pas utiliser ce correctif seul sur une version plus ancienne.

Fermer l’Activity puis la relancer après le déploiement. Aucune nouvelle variable, aucun changement de port, aucune réinitialisation du tutoriel ou des joueurs.

## Fonctionnement

Les effets s’ajustent aux dimensions de l’image, y compris sur mobile et après rotation. La couche décorative ne reçoit aucun clic et n’ajoute aucun bouton.

Les animations se mettent en pause dans un menu, pendant un changement de scène, lorsque l’onglet n’est plus visible et si le système demande une réduction des animations. Les autres lieux conservent leur affichage actuel.

La cadence de dessin est limitée à 24 images par seconde sur les petites vues et 30 sur les grandes, avec une résolution plafonnée. Aucun asset ou service réseau supplémentaire n’est nécessaire.

## Retour au hub statique

Réutiliser la version précédente « Boutons d’origine ». Les sauvegardes restent compatibles : cette mise à jour ne modifie que la présentation.
