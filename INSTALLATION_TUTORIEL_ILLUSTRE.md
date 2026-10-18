# Installation

Cette livraison part de Altherya_Connexion_Discord_Corrigee, version 23. Le ZIP complet contient le projet et ses assets ; le petit correctif contient les fichiers ajoutés ou modifiés, y compris les six illustrations.

Copiez le contenu du dossier Altherya_V0_8_10 dans votre projet, au niveau du Dockerfile existant. Acceptez les remplacements. Mettez à jour ensemble le frontend, l’API et les assets/tutorial. Conservez vos .env, vos variables Coolify, ACTIVITY_DB et son volume persistant. Faites une sauvegarde avant mise à jour.

Envoyez les fichiers sur GitHub puis redéployez dans Coolify afin de reconstruire le frontend. Aucune nouvelle variable n’est requise. Fermez complètement l’Activity puis relancez-la dans Discord : le nom d’affichage Discord doit être automatique et l’accueil illustré doit remplacer le formulaire de nom et les anciens panneaux.

La remise à zéro du tutoriel est automatique et unique pour cette révision. Il n’y a aucune commande DELETE à exécuter. Chaque joueur doit refaire le parcours, mais les anciennes récompenses restent marquées comme récupérées. Après validation, le joueur revient dans le registre admin de la nouvelle version. Un second déploiement de la même version ne force pas à nouveau le tutoriel.

Ce paquet ne modifie pas directement votre serveur. La bascule de la liste s’appliquera lorsque les nouveaux fichiers API seront déployés.
