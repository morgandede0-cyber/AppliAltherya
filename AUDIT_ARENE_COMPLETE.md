# Validation de l’arène complète

## Périmètre

Changements limités à l’arène Activity, ses routes et composants, les types échangés, les tests et cette documentation. Les tactiques sont isolées dans `apps/api/arena_combat.py` ; le moteur historique `arena_engine.py`, utilisé ailleurs, reste inchangé. Les assets d’origine sont réutilisés : cadre du panneau et boutons bleus dorés. Les champions se distinguent par noms, rôles, couleurs et médaillons de rang ; aucun nouveau portrait de personnage n’est annoncé.

## Vérifications automatisées

- Suite serveur : 196 tests réussis ; puis les 10 tests ciblés arène repassés après enrichissement du rapport conservé (combattants, techniques, événements, journal).
- Suite frontend : 78 tests réussis ; compilation TypeScript/Vite réussie.
- Tests ciblés : tactiques distinctes, intention verrouillée, phases uniques sans résurrection, dégâts réellement perdus, garde non comptée en cas de mort par saignement, abandon, recharge, classement plancher, dixième champion sans rang XI.
- Sauvegardes : règlement et rapport atomiques ; rollback sur échec d’écriture ; même requête rejouée sans deuxième gain ; historique et solde conservés après réouverture de la base. La relecture après un autre jeu reste sans mutation.
- Parcours navigateur : 61 contrôles réussis, aucune erreur JavaScript. PC 1440×900 et 1186×570 ; mobile 390×844 et 320×568. Préparation, techniques, garde, PV, journal, victoire, résultat, relecture, historique après rechargement, dernier rapport, abandon et seconde phase. Animations réduites vérifiées sur 320 px. Les panneaux restent dans la fenêtre sans débordement horizontal ; un défilement vertical permet de consulter les détails sur petit écran.
- Contrôle de non-régression : 18 contrôles navigateur réussis. accueil de l’arène, préparation des mises, accès ruelle/voleur ; aucun déplacement des boutons du hub.

Les états de test utilisent des bases temporaires, des joueurs de test et des injections de PV uniquement dans ces bases pour atteindre les résultats de manière déterministe. Ces manipulations ne sont pas des fonctions du jeu livré.

## Limites et conservation

Les simulations de combat ont servi à détecter des enchaînements trop fermés, pas à démontrer un taux de victoire réel. Une validation humaine sur la durée reste nécessaire pour affiner les tactiques. Les récompenses ne sont pas relevées pour compenser la difficulté.

Comparaison avec l’archive précédente : tutoriel, économie et prix, progression, campagne, expéditions, moteurs de sauvegarde, Dockerfile et assets restent identiques. Le bonus du tutoriel reste 100 Gold +25 XP ; outils et sac à 400 Gold. Aucun effacement de données. Les anciens combats terminés sans rapport détaillé ne sont pas reconstruits rétroactivement.

Tests réalisés sur serveur local et Chromium. L’authentification réelle Discord, le client natif Discord, l’hébergement Coolify distant et une économie Oddium externe ne sont pas validés par ces tests locaux.
