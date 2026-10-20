# Grimoire des techniques — livre interactif

## Fonctionnement

Le grimoire commence fermé, avec une nouvelle couverture assortie au cuir, aux ferrures et aux cristaux du livre existant. « Ouvrir le grimoire » révèle le sommaire, première page numérotée. Le sommaire est cliquable, filtrable (toutes/apprises/scellées), et indique le numéro de chaque technique. Chaque technique possède sa propre page avec statistiques du serveur, description, limites et condition d’acquisition. La couverture n’est pas numérotée.

Pages précédente/suivante, flèches du clavier et balayage horizontal tactile permettent la lecture. Les transitions utilisent une feuille et une couverture en perspective. Les contrôles sont bloqués pendant les 620 ms de transition ; la préférence de réduction des animations supprime ce délai et les mouvements. « Fermer le livre » revient à la couverture. Le retour au lieu d’origine reste disponible.

Le bouton « Techniques équipées », en bas du livre, affiche les quatre emplacements ensemble : rapide, puissante, ultime, garde. « Modifier » propose uniquement les techniques apprises et compatibles avec cet emplacement, y compris la technique de base. Le remplacement est confirmé et gratuit. L’ancienne technique reste disponible. Un combat actif ou une révision d’équipement devenue obsolète bloque la confirmation.

## Règles préservées

Seuls les boss de la tour tous les dix étages permettent de dérober une technique. La tour actuelle reste limitée à dix étages : Varkhaz est donc son seul boss donnant une technique. Les techniques de l’arène et les techniques de base sont conservées. Aucun changement des prix, récompenses, outils, bonus de tutoriel ou données de joueurs. Aucun changement du code serveur ou du schéma de sauvegarde.

## Audit et vérifications

- Archive source `Altherya_V0_8_11(6).zip` : 453 884 090 octets, 1 028 entrées, contrôle ZIP complet sans erreur.
- 281 tests serveur réussis, dont les protections de sauvegarde, l’économie et les règles de techniques de boss.
- 165 tests client réussis. Nouveaux cas : couverture et sommaire initial, pagination, quatre emplacements, choix des techniques acquises, confirmation/annulation, blocage en combat, navigation bloquée pendant une transition et nettoyage des animations lors d’un changement de menu.
- Compilation de l’API et des modules Python du bot ; compilation TypeScript et build Vite réussis. Imports du module relus ; signatures des interfaces existantes conservées.
- Parcours navigateur avec API réelle et base temporaire : PC 1440×900 et mobile émulé 390×844. Vérification du sommaire, d’une technique scellée, de l’absence de don à l’étage 1, de Varkhaz, de l’équipement de son Ultime et du remplacement par l’Ultime de base sauvegardé côté serveur.
- Contrôles visuels supplémentaires PC/mobile : couverture, sommaire, page de technique et vue compacte des quatre emplacements. Le conflit avec les styles globaux d’en-tête et de pied de page a été corrigé pour éviter le masquage des boutons.
- Les nouvelles archives sont contrôlées : intégrité ZIP, absence d’entrées dupliquées, concordance des fichiers modifiés et CRC identiques pour les fichiers non concernés.

## Assets et livraison

Nouvelle image `apps/game/public/assets/ashkar/grimoire-cover-v1.png`, générée avec l’outil intégré ImageGen, arrière-plan transparent. Le prompt complet, le mode et la référence sont conservés dans `grimoire-cover-generation.json` du même dossier. Le cadre ouvert et les emblèmes existants sont réutilisés. Aucun texte de jeu n’est figé dans la couverture.

La petite archive de mise à jour s’applique à la version source ci-dessus ; copier les fichiers en gardant leurs dossiers, puis reconstruire et redémarrer comme d’habitude. L’archive complète inclut tous les fichiers non concernés de la version source. Le nom du dossier racine historique est conservé pour permettre l’installation habituelle. Aucun secret, nouvelle base ou capture de joueur n’est ajouté.

## Limites

Mobile vérifié par émulation navigateur, pas sur téléphone physique. Aucun déploiement distant, session Discord de production ou connexion à la base Gold Oddium de production effectué. Le build conserve l’avertissement existant de bundle supérieur à 500 kB ; il réussit. Les visuels de contrôle ne sont pas des fichiers de production.
