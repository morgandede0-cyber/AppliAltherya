# Correctif des animations du hub — 16 octobre 2026

Les effets existants étaient très discrets. Ils pouvaient aussi être arrêtés par la préférence système de réduction des animations. Le code précédent était bien présent sur le site public ; la cause exacte sur l'appareil du joueur n'est pas établie.

Cette version renforce la fumée de cheminée, les lumières et les reflets mobiles de la fontaine. Le bouton « Animations ✓ » dans la barre du haut permet de mettre les effets en pause. « Activer l’animation » les démarre, même si la préférence système réduit les animations. Ce choix est mémorisé sur cet appareil. Sans choix explicite, la préférence système reste respectée.

## Installation

- Archive complète : utiliser le contenu du dossier Altherya_V0_8_10 pour la mise à jour habituelle du dépôt, puis redéployer dans Coolify.
- Correctif léger : copier les fichiers de l'archive à la racine du projet existant, puis effectuer la même mise à jour et le redéploiement.
- Conserver le fichier .env et le volume de données existants. Ne pas remplacer la base de données.
- Après le déploiement, fermer puis rouvrir l'Activity. Au besoin, cliquer sur « Activer l’animation » dans la barre du haut.

Les effets s'arrêtent lorsque le hub est caché par un menu ou que l'onglet est masqué. Ils reprennent ensuite. L'image originale et les positions des boutons restent conservées. Aucun changement du serveur, des soldes ou de la configuration Discord.

Cette livraison doit être redéployée pour apparaître sur le site. Elle ne déploie pas automatiquement sur Coolify.
