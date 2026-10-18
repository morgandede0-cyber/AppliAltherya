# Menus — correction du 10 octobre 2026

Les images de menus approuvées sont conservées. Leur taille tient compte de la hauteur réelle de la fenêtre et du bandeau du joueur. Les valeurs et zones interactives sont placées dans les ornements d’origine, sans les anciens fonds rectangulaires.

Le marchand utilise des cartes à informations réelles, quatre articles au maximum par page et des objets d’histoire séparés avec leur chapitre. La forge conserve ses boutons graphiques et centre les équipements et les coûts. La banque, le marchand et les annonces possèdent une disposition lisible sur téléphone. Les opérations bancaires sont reliées aux actions serveur existantes.

## Installation du correctif
Décompresser Correctif_Menus_propres.zip dans le dossier du projet : le dossier apps du correctif doit fusionner avec le dossier apps existant. Accepter le remplacement des fichiers. Lancer votre fichier habituel de mise à jour GitHub puis redéployer dans Coolify. Ne remplacer ni .env ni la base de données.

## Vérifications
Compilation TypeScript et Vite réussie. 34 tests client et 36 tests API réussis. Vérification des limites des menus dans Chromium : 1186×691, 1186×570 et 390×844. Dépôt et retrait vérifiés dans le navigateur avec une base de test isolée ; passage de la disposition mobile à la disposition ordinateur vérifié. La revue visuelle porte sur des états de test, les chiffres affichés proviennent de leur snapshot.

Le fichier src/data/rules.ts est inclus : il manquait dans l’archive précédente. Le correctif ne modifie pas les comptes ni les données de production.
