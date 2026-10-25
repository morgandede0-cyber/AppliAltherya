# Inventaire séparé du profil

Le médaillon Inventaire ouvre directement le mode inventaire, sans afficher puis basculer le profil. Le menu contient uniquement ressources, objets d’histoire, filtres, tri, pagination et informations des objets. Le pied de page possède un seul bouton Fermer.

Carnet d’aventurier, Mon personnage, Historique des combats, Refaire le tutoriel et Retour au hub sont retirés de cette vue. Le profil et ses commandes restent accessibles depuis le portrait. Les objets d’histoire restent séparés, avec leur chapitre. La limite de quatre objets par page et la conservation du tri/de la page pendant une actualisation restent en place.

Aucun changement de backend, d’inventaire sauvegardé, de prix, de Gold ou de récompense. Le tutoriel reste explicatif.

Vérifications : 255 tests client et construction TypeScript/Vite réussis. Tests du profil, de l’ouverture directe, de la séparation des objets et de l’actualisation. Parcours navigateur des hotbarres et des livres en 1440×900, 1186×570, 390×844 et 320×568, avec assertions supplémentaires sur l’absence de fiche personnage et la présence d’un seul bouton Fermer dans l’inventaire. Le journal des mises à jour est mis à jour et ses tests d’ouverture/pagination/détails passent.

Les tests utilisent une base temporaire et des comptes fictifs. Aucun accès à la base de production ni déploiement. Mise à jour cumulative à copier sur le projet existant, puis reconstruire et redéployer avec Coolify ; recharger l’Activity ensuite.
