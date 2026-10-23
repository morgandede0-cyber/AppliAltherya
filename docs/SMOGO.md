# Smogo — les énigmes à mise

Accès : Ruelle sombre → Smogo. Aucun changement de variable d’environnement. Les tables sont créées automatiquement au démarrage de l’API.

## Règles

Le joueur confirme une mise de 1 à 25 Gold avant de découvrir la question. Il dispose de 120 secondes et d’une seule réponse, avec confirmation. Une bonne réponse rend deux fois la mise (mise initiale + bénéfice égal à la mise). Une mauvaise réponse, un abandon ou un délai dépassé perd uniquement la mise déjà prélevée. Trois parties sont permises par journée du calendrier de Paris. Aucune XP n’est attribuée.

## Apparitions

Trois passages d’une heure sont tirés chaque jour, un dans chaque tiers de la journée civile de Paris. Les horaires sont communs à tous les joueurs et enregistrés en base ; ils ne sont pas exposés à l’avance. Entre les passages, le bouton disparaît et le serveur refuse les nouvelles mises. Une partie payée reste accessible et réglable jusqu’à sa fin. Une présence affichée peut être actualisée avec la cadence habituelle de 15 secondes, mais le serveur contrôle immédiatement chaque nouvelle mise.

## Questions et reprise

Chaque question concrète est réservée dans une table globale au moyen de son empreinte : deux parties validées ne reçoivent pas le même texte normalisé. Une banque de 100 énigmes et devinettes rédigées, complétée par des variantes numériques fournissent les questions. Une impossibilité de réserver une question annule la transaction entière, prélèvement compris.

La question, la mise et l’échéance sont enregistrées côté serveur sous l’identité canonique du joueur. Fermer le menu, recharger ou revenir avec une autre session Discord du même compte conserve la partie. Le chronomètre continue pendant l’absence ; changer de jour ne permet pas de remplacer une partie active. Les réponses et explications restent privées jusqu’au résultat.

## Sécurité

Débit et réservation sont atomiques. La révision, l’identifiant de partie, les reçus d’idempotence et l’état enregistré empêchent les doubles règlements et les réponses à la partie d’un autre joueur. Le serveur décide du résultat et de l’échéance. Les fermetures de maintenance globales, de la ruelle et de Smogo sont respectées, ainsi que le tutoriel obligatoire.

## Livraison

Mise à jour cumulative Popie + Panda + Smogo à superposer au projet existant, puis reconstruire et redéployer selon la procédure habituelle. Ne pas remplacer les données persistantes ni les fichiers d’environnement. Aucun déploiement en production n’est effectué par ce livrable.
