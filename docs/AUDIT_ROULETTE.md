# Audit roulette européenne

- Construction TypeScript/Vite réussie.
- Compilation syntaxique des 84 modules Python réussie.
- Suite serveur complète : 229 tests réussis, 0 erreur et 0 échec.
- Suite interface : 121 tests réussis, aucun échec.
- Parcours navigateur roulette : 60 contrôles sur PC, petit PC et deux mobiles (1440×900, 1186×570, 390×844 et 320×568). Mises multiples, Annuler, carte des cases, blocage des actions et d’Échap, animation visible, somme des retours, solde, poche d’arrivée, règles et navigation vérifiés.
- Régression navigateur du blackjack : 32 contrôles réussis sur les mêmes quatre dimensions.
- Tests des 37 destinations de la bille, continuité de trajectoire, zéro et couleurs. Tests serveur de validation, gains cumulés, compatibilité des anciennes requêtes et absence de double règlement.
- Inspection visuelle PC/mobile et paysage mobile ; numéros exacts en code, textures et jetons indépendants du décor.

Les tests utilisent des bases SQLite temporaires. Aucun essai sur les soldes de production ni sur la connexion Oddium en production. Pas de test dans le client Discord de production. Les autres jeux, les récompenses du tutoriel et le prix des outils restent inchangés.

La trajectoire est une animation contrôlée aboutissant au résultat serveur, avec décélération et rebonds visuels ; pas un moteur physique libre. Le décor et le croupier restent fixes. Roulette à zéro unique, sans partage ni prison.
