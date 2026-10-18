# Audit : techniques des champions

## Changements

Collection permanente de dix techniques, déblocage uniquement après de nouvelles victoires (le rattrapage initial est remplacé par le reset unique décrit dans INSTALLATION_RESET_CHAMPIONS.md), équipement à quatre emplacements, comparaison et confirmation de remplacement. Le résultat de victoire annonce la technique nouvellement acquise. Les effets sont résolus côté serveur, avec les techniques équipées figées au départ du duel. Le moteur historique du bot et de la campagne reste inchangé ; un adaptateur de combattant et un module Activity ajoutent les effets sans modifier ses classes globales.

## Vérifications

Suite serveur : 207 tests réussis ; puis 12 tests ciblés réussis après le dernier ajustement du journal de garde avec saignement. Suite frontend : 79 tests réussis. Compilation Python et build TypeScript/Vite réussis.

- Compilation de tous les modules Python des apps API et bot ; TypeScript et build Vite.
- Tests serveur des dix effets et de leurs contreparties : saignement, esquive, charge, réduction de garde, riposte, traversée de garde, seuil d’exécution, affaiblissement et contrecoup.
- Tests de possession, emplacement incompatible, version périmée, séparation des joueurs, interdiction d’équiper en combat, conservation après redémarrage, conservation des acquisitions après redémarrage, restauration gratuite de la technique de base.
- Victoire : déblocage unique ; défaite/abandon : aucun déblocage. Échec d’écriture : rollback du duel, des gains, de la progression et du déblocage. Les tests de règlement, de requête rejouée et d’historique de l’arène restent inclus.
- Interface : confirmation/annulation, verrouillage pendant la requête et pendant un duel, transmission de la version d’équipement, anciennes techniques conservées.
- Parcours Chromium : 69 contrôles réussis, aucune erreur JavaScript, sur 1440×900, 1186×570, 390×844 et 320×568 : guide, victoire, acquisition, grimoire, annulation puis remplacement réel, conservation du solde, résultat et prochain combat. Régression des mises, de la ruelle et des panneaux : 18 contrôles navigateur réussis.
- Comparaison à la version précédente : tous les assets, le hub, les prix, le tutoriel, la campagne, les expéditions et les moteurs historiques de sauvegarde et de combat restent identiques.

Les bases, captures et injections de PV utilisées pour atteindre les cas de test restent locales et ne sont pas livrées. Le correctif contient les sources et les tests, pas une base de joueurs.

## Limites

Les effets ont des tests déterministes ; l’équilibrage humain sur des séries de combats n’est pas démontré. Il pourra être ajusté sans supprimer les techniques acquises. Tests locaux uniquement : ni déploiement Coolify, ni client natif Discord, ni connexion à une économie distante Oddium validés ici. Les sauvegardes SQLite de l’Activity sont conservées.
