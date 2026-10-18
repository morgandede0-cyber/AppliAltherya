# Audit du tirage des quotidiennes

Le choix des tâches est effectué dans CastleStore, puis sauvegardé avec une clef unique joueur/jour. Les accès concurrents utilisent un insert-or-ignore et relisent le tirage réellement conservé. La progression et l’attribution des récompenses restent côté serveur. La récupération examine aussi les anciennes lignes déjà récompensées pour empêcher une seconde attribution après migration.

La récompense de connexion est lue depuis last_daily, état déjà autoritaire du profil. Aucun nouveau crédit client. Les cibles d’expédition restent génériques et réalisables au départ. La variation du combat et de la quantité de jeux ne demande aucun déblocage.

Vérifications : compilation Python API et bot ; compilation TypeScript et build de production ; 65 tests frontend ; neuf tests ciblés des quotidiennes couvrant stabilité, lectures concurrentes, changement entre jours, diversité entre joueurs, exclusions, récompense unique et migration. 165 tests API réussis et 23 contrôles navigateur réussis.

23 contrôles navigateur ont réussi sur PC 1440 × 900 et 810 × 465, mobile 390 × 844 et 320 × 568, sans erreur JavaScript. La disposition des deux panneaux est conservée.

Limites : environnement local, sans déploiement Coolify ni authentification réelle Discord. L’économie partagée avec Oddium n’a pas été validée. Le nouveau scénario reste séparé. Aucun asset, secret, port ou règle de butin n’a été modifié.
