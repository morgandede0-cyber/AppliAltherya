# Tutoriel à douze étapes — mise à jour cumulative

Copier les fichiers du dossier Altherya_V0_8_10 dans le projet existant en acceptant leur remplacement. Conserver les autres fichiers du projet, les variables d’environnement, la base et les sauvegardes.

Reconstruire le frontend et redéployer l’application via votre procédure Coolify habituelle, avec redémarrage de l’API.

Après redéploiement et redémarrage de l’API, tous les joueurs doivent refaire le nouveau tutoriel depuis l’étape 1. La liste admin des tutoriels terminés est vide pour cette nouvelle révision, puis se remplit au fur et à mesure des validations.

Cette remise à zéro s’applique une seule fois à cette version. Les reconnexions et redémarrages suivants conservent la progression. Les récompenses déjà reçues restent enregistrées : ni Gold ni XP supplémentaires pour les anciens joueurs. Les nouveaux joueurs conservent le bonus normal de 100 Gold et 25 XP.

Aucune commande SQL manuelle ni suppression de base n’est nécessaire. Aucun changement des soldes, inventaires, quêtes ou équipements.

Les anciens visuels page-0.png à page-5.png et guide-skin-v2.png ne sont plus utilisés ni livrés. La reconstruction les retire automatiquement de apps/game/public/assets/tutorial, y compris après une copie de mise à jour ; les seuls fichiers nécessaires dans ce dossier sont wolf-scenes-1.png, wolf-scenes-2.png, wolf-scenes-3.png et wolf-button.png.

Documentation et bilan : docs/TUTORIEL_GUIDE_20261024.md et docs/AUDIT_TUTORIEL_12_ETAPES.md.
