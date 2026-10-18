# Audit — Journal des mises à jour

## Livraison
Le bouton Panneau central ouvre le nouveau journal. L’ancien journal d’aventure
reste accessible depuis les autres routes existantes ; le panneau central
n’affiche plus les activités, objectifs, soldes ou récompenses quotidiennes.
Cadre original généré pour cette interface, extérieur transparent, fond bleu sombre,
lanternes, frise de dates et cartes interactives. Texte et dates ne sont pas gravés
dans l’image. Illustration du contrat dédiée à la première annonce.
Trois annonces par page, développement/repli au clic, gestion du focus, Échap,
retour au hub. Les rafraîchissements du personnage ne réinitialisent pas la lecture.

## Vérifications automatiques
- TypeScript strict et compilation Vite : succès.
- 81 tests frontend : succès, dont deux tests du journal (développement,
  changement de page, état conservé, liste vide et fermeture).
- 220 tests serveur : succès.
- Compilation Python de apps/api et apps/bot : succès.
- 32 contrôles Playwright : succès, aucune erreur JavaScript ; formats 1440×900,
  1186×570, 390×844 et 320×568. Ouverture depuis le hub, panneau dans le viewport,
  contenu sans débordement horizontal, repli/dépli, fermeture et conservation des soldes.
- Inspection visuelle des captures PC et mobile ; adaptation de la frise sur mobile.
- Comparaison de l’archive complète à la version précédente : seuls les fichiers du
  journal, son raccordement au hub, la commande de test et cette documentation changent.
- Vérification CRC des deux ZIP et exclusion des bases de données et dépendances.

## Limites
Pas de déploiement distant ni de test dans le client Discord connecté réel.
Les notes se publient en modifiant update-notes.ts puis en redéployant ; aucun
éditeur admin de notes n’a été ajouté. Les flèches sont désactivées avec une seule
page (trois notes actuellement) et s’activent automatiquement avec d’autres notes.
Les sauvegardes, migrations, prix, récompense du tutoriel, jeux et progression
ne sont pas modifiés. La base existante reste SQLite isolée ; aucune connexion
réelle à une économie PostgreSQL partagée avec Oddium n’est ajoutée ni validée.
Les illustrations ont été générées avec l’outil d’image intégré : cadre vide en
bois/bronze et fond bleu sombre, puis parchemin scellé avec plume et encrier.
