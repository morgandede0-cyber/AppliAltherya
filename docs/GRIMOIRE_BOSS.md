# Grimoire des techniques et boss de palier

Le menu des techniques est un grimoire ancien, illustré sur fond transparent. Une page par technique : bases, dix champions de l’arène et boss de tour. Statistiques calculées par le serveur, description, limites, origine et condition de déblocage restent consultables pour les techniques scellées. Sommaire, filtres, navigation clavier et retour au lieu d’origine. La lecture défile dans le parchemin sur les petits écrans.

Équipement gratuit avec confirmation de l’ancien et du nouveau choix ; l’ancienne technique reste apprise. Le serveur vérifie l’emplacement, l’acquisition, l’absence de combat actif et la révision de l’équipement. Les doubles clics sont bloqués pendant l’envoi.

## Tour

Seuls les boss tous les dix étages donnent une technique. Les dix étages actuels comportent donc une seule technique de tour : **Serment de Varkhaz**, étage 10, emplacement Ultime. Aucun étage 20 ou supérieur n’a été ajouté. Les techniques de champions restent disponibles.

Au démarrage, les techniques des étages intermédiaires sont retirées de la collection et des emplacements. Les techniques de base correspondantes les remplacent. La migration conserve les soldes, XP, progression, quota, PV et recharge. Elle nettoie aussi les compétences et anciens messages de récompense dans les combats sauvegardés, sans recommencer les combats. Un second démarrage ne réapplique pas les changements. Un ancien joueur peut rejouer le boss de l’étage 10 pour apprendre sa technique manquante ; aucune récompense économique répétée.

## KHAZ’GORAM

Les six pièces communes de chaque voie, arme comprise, coûtent 1 000 Gold chacune. Tarifs alignés côté API et bot ; le serveur ignore un prix envoyé par le client. Les prix des outils, coûts Pouciels et équipements déjà possédés restent inchangés.

## Installation

Appliquer la mise à jour sur la version précédente, conserver la base existante et les variables d’environnement, puis reconstruire et redémarrer suivant la procédure habituelle. Le ZIP complet contient aussi les autres fichiers du projet. Aucun secret ni base de joueurs n’est inclus. Aucun déploiement de production réalisé.

## Asset

`apps/game/public/assets/ashkar/technique-grimoire-v1.png` : image créée avec ImageGen, génération originale, arrière-plan transparent. Direction artistique : grimoire ancien de la tour d’Ashkar, parchemin vierge unique, cuir ancien, ferrures sombres, détails de cristal bleu, espace de lecture clair. Les textes et commandes sont de vrais éléments interactifs, absents de l’image.

## Vérifications

281 tests serveur et 163 tests client réussis ; compilation Python et TypeScript/Vite réussie. Le parcours navigateur avec API réelle et base temporaire vérifie les menus sur ordinateur (1440×900) et mobile (390×844), les pages du grimoire et l’absence de technique à l’étage 1. Les tests serveur couvrent l’acquisition de Varkhaz, l’usage dans les deux lieux, les remplacements et la migration sans perte de progression. L’achat commun à 1 000 Gold et l’amélioration Pouciel ont également été vérifiés dans le navigateur aux deux tailles. Les captures du grimoire ont été inspectées. La session Discord de production n’a pas été testée.

Le parcours navigateur confirme aussi, aux deux tailles, la victoire contre Varkhaz, l’ouverture directe de sa page, la confirmation du remplacement et la présence de `ashkar_10` dans l’emplacement Ultime sauvegardé côté serveur.
