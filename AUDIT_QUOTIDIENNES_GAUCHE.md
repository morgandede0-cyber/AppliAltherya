# Audit — quotidiennes classiques et panneau gauche

Compilation TypeScript et build de production réussis. 65 tests frontend réussis. 160 tests API réussis, dont quatre tests du système quotidien : trois objectifs accessibles au départ, récompense tout-ou-rien, unicité après redémarrage, et absence de double récompense après une ancienne journée à six objectifs.

23 contrôles Chromium réussis sur 1440 × 900, 810 × 465, 390 × 844 et 320 × 568. Vérification des côtés gauche/droite, des limites d’écran, des compteurs, de l’ouverture des menus et du repli mutuel sur mobile ; aucune erreur JavaScript. Captures inspectées localement.

Compilation des modules Python API et bot réussie. Retrait des anciennes tables de difficulté et du calcul de réputation devenus inutiles pour les quotidiennes. Compteurs du château et messages du bot adaptés au nombre réel d’objectifs. Aucun changement des tables de butin, des règles de destination ni des positions du hub.

Les tests locaux couvrent la base SQLite du projet. Ils ne valident pas le Gold partagé avec Oddium ni un déploiement réel sur Coolify ou une session OAuth Discord. La campagne narrative n’est pas intégrée. Les rapports plus anciens dans l’archive décrivent leurs livraisons respectives ; ce document décrit le présent correctif.
