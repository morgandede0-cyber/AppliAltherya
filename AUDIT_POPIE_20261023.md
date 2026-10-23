# Livraison Popie — 23 octobre 2026

Popie est intégrée au projet complet, à partir de la version 17 de l’archive de référence. Accès par les entrepôts du Port des Brumes, dont le verrouillage narratif est conservé.

## Changements

- Scène, portrait détouré, panneau et bouton assortis.
- Trois services interactifs : commandes, échanges et livraisons.
- Confirmation avant toute remise de ressources ; compteur de livraison en minutes et secondes.
- Sauvegarde personnelle additive et paiement atomique. Limites quotidiennes calculées à Paris.
- Résultat fixé au départ et conservé sans être exposé au client. Aucun résultat ou montant fourni par le client n’est utilisé.
- Maintenance existante appliquée au lieu. Journal central mis à jour avec les fonctions livrées.
- Tutoriel, prix des outils, récompenses existantes et objectifs de la campagne conservés.

Les règles et les montants sont détaillés dans `docs/POPIE.md`.

## Vérifications automatisées

- Compilation des modules Python API et bot : réussie.
- TypeScript et production Vite : réussis. Avertissement Vite préexistant sur la taille de certains fichiers JavaScript.
- Suite interface : 188 tests réussis.
- Tests ciblés interface après ajustements : 8 réussis, dont confirmations, compteur et rendu littéral des textes ; journal central et dossier du port.
- API Popie : 10 tests réussis (accès, scène, révision, double requête, concurrence, inventaire insuffisant, conservation après redémarrage, récupération anticipée, échec risqué, changement de jour, maintenance et limite du portefeuille).
- Régression port : 17 tests réussis.
- Régression activité : 11 tests réussis (banque, achat, expédition, contrat, ventes, histoire, passerelle HTTP).
- Persistance économique : 13 tests réussis.
- Bot : 17 tests réussis. Un avertissement de fichier non fermé dans le test historique du tableau de bord est présent ; aucun échec.

## Contrôle navigateur

Le parcours Playwright vérifie les commandes avec confirmation, un échange, le démarrage d’une livraison, le blocage du retrait anticipé et la conservation au retour au comptoir. Les contrôles mesurent les débordements horizontaux et les boutons de retour. Le parcours complet a réussi 24 contrôles sur 1440×900, 1186×570, 390×844 et 320×568, sans erreur JavaScript. Les captures ont servi à corriger les styles hérités des onglets et l’espace intérieur du panneau ; la dernière passe sur la version livrée réussit les quatre tailles d’écran, sans erreur JavaScript. Les captures PC et mobile ont été inspectées : les onglets sont séparés et centrés, le contenu reste dans le panneau et les boutons de retour dans la fenêtre. Le contenu peut défiler dans le cadre lorsque la place manque.

## Limites

Tests réalisés avec des comptes et bases temporaires locaux. Pas de connexion au serveur Discord, à Coolify, au PostgreSQL d’Oddium ni aux données réelles des joueurs. La livraison est un projet à déployer avec le processus habituel ; aucun déploiement de production n’a été effectué. Les tests locaux ne constituent pas une garantie d’absence de tout défaut.
