# Audit du nouveau profil

## Changements
Profil dédié utilisant le cadre et la palette du Journal d’Altherya. Données
interactives : identité Discord vérifiée, niveau, XP, portefeuille, banque,
équipement réel, parcours et réputations. Les absences d’équipement sont visibles.
L’ancien rendu du profil et ses variables devenues inutiles ont été retirés.
Inventaire : catégories séparées, quatre entrées par page, état maintenu pendant
l’actualisation et défilement réinitialisé lors d’un changement de vue ou de page.
Les noms sont insérés comme texte. Si l’avatar échoue, les initiales sont conservées.
Une note de mise à jour datée du 18 octobre figure dans le journal.

## Vérifications
- Compilation TypeScript stricte et Vite réussie.
- 83 tests frontend réussis ; tests dédiés sur les données dynamiques, le surnom,
  l’avatar, son secours, les équipements absents, l’inventaire et la pagination.
- 26 tests du service de surnoms serveur et 8 tests de profils Discord réussis.
- 36 contrôles navigateur sur le profil et l’accès admin par surnom : quatre
  formats 1440×900, 1186×570, 390×844, 320×568 ; aucune erreur JavaScript.
  Avatars simulés pour tester chargement réussi et erreur 404 sans solliciter Discord.
- Régression du Journal des mises à jour : 32 contrôles navigateur réussis.
- Inspection visuelle PC et mobile. Les petits écrans font défiler le contenu
  à l’intérieur du cadre ; le pied du menu garde les commandes accessibles.
- Compilation Python réussie ; code serveur et schémas de base inchangés.
- La suite complète des 220 tests serveur avait passé lors de la livraison du
  journal précédent ; seuls les 34 tests d’identité ont été relancés ici.
- Comparaison de l’archive à la livraison précédente et contrôle CRC des ZIP.

## Limites et conservation
Le serveur Discord réel et son CDN n’ont pas été testés avec un compte connecté.
Le surnom dépend du service existant, de l’accès du bot au serveur et de ses
variables existantes. Le profil ne réclame aucun nouvel accès administrateur.
Pas de déploiement distant, pas de reset, pas de modification de prix, de récompense
ou de sauvegarde. L’économie reste SQLite isolée ; le partage PostgreSQL/Oddium
n’est pas ajouté ni validé. Le chapitre d’un objet est indiqué quand le catalogue
retourné par le serveur en fournit la correspondance.
