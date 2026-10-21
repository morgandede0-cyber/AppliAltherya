# Vérifications du blackjack

- Construction TypeScript et Vite réussie.
- Compilation syntaxique des 82 modules Python : réussie.
- Suite serveur complète : 224 tests réussis, aucune erreur.
- Suite interface : 115 tests réussis, aucune erreur.
- Parcours navigateur avec API réelle et SQLite temporaire : 32 contrôles réussis sur 1440×900, 1186×570, 390×844 et 320×568. Distribution, verrouillage des actions, carte cachée, résultat, cohérence du Gold et retour à la salle vérifiés.
- Inspection visuelle finale : PC, petit PC, mobile et paysage mobile. Cartes décodées et boutons détourés vérifiés.
- Doublement : tests serveur dédiés pour carte unique, débit supplémentaire unique, règlement exact, dépassement de 21, refus après tirage et solde insuffisant.
- Identifiants de révision et règles de règlement serveur préservés. Les 52 SVG sont déterministes ; aucun tirage aléatoire côté navigateur.
- Les autres jeux, le bonus du tutoriel, les prix des outils, les autres menus et les variables d’hébergement ne sont pas modifiés.

Limites : variante sans partage ni assurance. Croupier et décor fixes ; animations des cartes, retournement et jetons. Pas de validation dans le client Discord de production ; tests locaux Chromium avec API réelle et base temporaire. La base de production et la connexion Gold d’Oddium n’ont pas été utilisées pendant les tests.
