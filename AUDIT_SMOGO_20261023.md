# Validation Smogo — 23 octobre 2026

## Résultats

- API Smogo : 20 tests réussis, incluant les débits/remboursements, doubles requêtes concurrentes, idempotence, données privées, questions distinctes entre joueurs, reprise après redémarrage et seconde session Discord canonique, délai serveur, changement de jour, limites de mise et maintenance.
- Régression Activity : 11 tests réussis.
- Régression économie et sauvegardes : 13 tests réussis.
- Interface : suite complète de 195 tests réussis ; après le dernier ajustement de placement, 12 tests ciblés Smogo, navigation et journal réussis.
- Compilation TypeScript/Vite finale réussie. Avertissement historique sur la taille de certains bundles.
- Compilation Python API et bot réussie.
- Navigateur Chromium sur le build final : 31 contrôles réussis, aucune erreur JavaScript. Formats 1440×900, 1186×570, 390×844 et 320×568. Parcours réel hub → ruelle → Smogo, confirmation avant débit, absence de réponse privée, réouverture conservant question/mise/échéance, rechargement complet PC et mobile, succès/échec et soldes attendus, quatre questions distinctes, panneau et retour contenus dans la fenêtre.
- Captures PC et mobile inspectées : personnage et scène intégrés, panneau lisible ; contenu mobile défilant avec retour accessible.

## Portée

Tests locaux sur base SQLite temporaire avec comptes Discord canoniques simulés. Aucun compte réel, secret de bot, envoi Discord ou base de production utilisé. Ces vérifications ne remplacent pas une validation après déploiement sur votre hébergement et dans l’Activity Discord réelle. Les données persistantes existantes doivent rester montées et conservées lors du redéploiement.

La réservation globale protège l’unicité des textes concrets dans la base conservée ; les familles numériques restent des variantes d’un même type de problème. Le temps de 120 secondes continue pendant l’absence. Pas de récupération de mise par fermeture/reconnexion. Aucun changement du bonus tutoriel, des prix d’outils ou des autres récompenses.

## Extension — bibliothèque et apparitions

- Banque vérifiée : exactement 100 énigmes rédigées, identifiants et questions uniques, réponses et explications non vides. Les variantes numériques restent disponibles en complément.
- Suite API étendue : 24 tests réussis. Nouveaux contrôles : refus des mises en l’absence de Smogo sans débit, partie payée conservée et réglable après sa disparition, trois passages quotidiens distincts d’une heure, limites de début/fin et conservation du planning après redémarrage.
- Interface complète : 197 tests réussis, incluant absence de formulaire pendant l’absence, maintien du formulaire d’une partie payée, annulation d’une confirmation devenue périmée.
- Build TypeScript/Vite et compilation Python réussis. Les règles de mise, délais, récompenses et limites quotidiennes restent celles de la version précédente.
- Nouveau contrôle sur le build final en navigateur : 31 vérifications réussies sur les quatre formats PC/mobile, sans erreur JavaScript. Les passages sont fixés dans la base temporaire pour rendre ces parcours reproductibles.
- Scénario navigateur supplémentaire : 10 vérifications réussies, sans erreur JavaScript. Smogo est retiré du planning après la mise, le joueur quitte puis recharge le jeu, retrouve sa partie, répond correctement et reçoit exactement son gain ; une fois réglée, le bouton Smogo n’est plus visible dans la ruelle.
