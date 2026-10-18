# Althérya — lancement royal et affichage adaptatif

## Installation

1. Décompresser l’archive complète et ouvrir le dossier `Altherya_V0_8_10`.
2. Copier son contenu dans le dépôt du jeu puis effectuer la mise à jour habituelle GitHub.
3. Redéployer dans Coolify avec reconstruction du frontend. Conserver les variables et le volume de données actuels.
4. Fermer l’Activity et la relancer pour récupérer la nouvelle interface.

Aucune nouvelle variable d’environnement, aucun changement de port, aucune remise à zéro du tutoriel ou des joueurs.

Le correctif seul contient uniquement les fichiers modifiés et ce guide : copier son contenu sur la version précédente « Pseudos serveur ». Si la base installée est plus ancienne, utiliser le projet complet.

## Comportement

- Lancement au blason royal transparent, décor flouté, barre bleue animée, étapes Discord / Personnage / Monde.
- La progression suit les jalons de connexion, la réponse du profil et les images du hub. Les valeurs correspondent à des étapes pondérées, pas à un chronomètre ni à un débit de téléchargement. 100 % n’est atteint qu’après chargement du hub.
- Hors Activity, l’indicateur Discord devient « Session ». Un serveur exigeant Discord conserve cette exigence.
- Erreur de connexion ou image inaccessible : message lisible et bouton Réessayer, sans faux passage à 100 %.
- Placement d’origine restauré sur les bâtiments dans tous les formats. Les grilles portrait et le dock paysage sont supprimés.
- Décor affiché entièrement à ses proportions d’origine ; les zones cliquables restent alignées avec lui lors d’une rotation ou d’un redimensionnement.
- Bandeau du joueur plus compact, nom serveur et valeurs réelles du profil.

## Vérification après déploiement

Lancer depuis Discord, vérifier le chargement et l’accès au personnage habituel. Tester Banque et retour au hub, puis tourner le téléphone. Les vérifications locales détaillées et les limites sont consignées dans `AUDIT_LANCEMENT_PC_MOBILE.md`.
