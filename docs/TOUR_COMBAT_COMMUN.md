# Tour d’Ashkar : combat et techniques partagés avec l’arène

Le combat et l’interface de l’arène sont réutilisés directement. Les deux lieux partagent le journal structuré, les intentions adverses, les gardes, états, saignements, esquives, recharges, statistiques de combat, animations des PV et confirmation d’abandon. Le bilan de la tour affiche ses vrais Gold, XP et Pouciels ; aucun classement ni pari d’arène n’est appliqué.

Chaque gardien possède sa propre technique et peut l’utiliser contre le joueur. La première victoire contre lui l’ajoute gratuitement à la collection commune. Les techniques ont les mêmes effets et limites dans les deux lieux ; elles évoluent avec les techniques de base du joueur. Elles ne sont pas équipées automatiquement. Quatre emplacements : rapide, puissante, ultime, garde. Remplacer une technique conserve l’ancienne. Le remplacement est interdit pendant un combat actif et validé par révision côté serveur.

| Étage | Technique | Emplacement | Effet |
|---|---|---|---|
| 1 | Morsure infectée | Puissante | Saignement |
| 2 | Feinte du pillard | Rapide | Esquive temporaire |
| 3 | Pas spectral | Garde | Protection et esquive |
| 4 | Rempart déchu | Garde | Forte garde, prochaine attaque réduite |
| 5 | Fracas des cavernes | Puissante | Adversaire ébranlé |
| 6 | Furie du berserker | Rapide | Prochaine attaque renforcée |
| 7 | Lame corrompue | Ultime | Perce une partie de la garde |
| 8 | Riposte d’obsidienne | Garde | Prépare une riposte après impact |
| 9 | Sentence des abysses | Ultime | Renforcée sur cible affaiblie |
| 10 | Serment de Varkhaz | Ultime | Renforcée à bas PV, contrecoup |

## Progression préservée

Accès niveau 5, dix étages, trois **nouvelles validations** par jour et récompenses économiques inchangés. Les étages acquis et toutes les compétences de l’arène restent acquis. Aucun reset et aucun déblocage rétroactif automatique.

Les étages déjà validés sont rejouables depuis « Les dix étages ». Cela permet aux anciens joueurs de gagner une technique manquante sans effacer leur progression. Une revanche ne verse aucun Gold, XP ou Pouciel, ne crée pas une nouvelle validation et ne consomme pas le quota des nouveaux étages. La technique ne peut être gagnée qu’une seule fois, y compris en cas de requêtes simultanées.

Les combats commencés sur l’ancien moteur sont convertis à la prochaine action, en conservant la proportion de PV, la recharge et le journal. Les anciens bilans restent consultables sur l’ancien écran ; les prochains combats utilisent l’écran partagé. Les gardiens disposent de PV fixes sur l’échelle de l’arène : anciens PV divisés par six, arrondis (108 à 317). Leurs profils et intentions sont fixes par étage. Aucune adaptation cachée au niveau du joueur.

## Vérifications et livraison

276 tests serveur et 162 tests client réussissent, ainsi que la compilation Python et TypeScript/Vite. Les tests couvrent les effets du moteur partagé, l’apprentissage dans la tour puis l’usage dans l’arène, les compétences verrouillées/incompatibles, le remplacement et la sauvegarde, le combat figé, la revanche sans récompense répétée, les anciens étages et la conversion d’un ancien combat. Le parcours navigateur vérifie l’ensemble sur ordinateur et mobile, avec une base temporaire et des PV ennemis réduits uniquement pour accélérer les victoires de test. Les captures sont inspectées ; la version mobile garde les PV visibles pendant le défilement des commandes.

L’archive de mise à jour s’applique à la version avec la tour déjà ouverte. Le projet complet contient toutes les évolutions. Sauvegarder la base puis redéployer normalement. Aucun fichier de joueurs ni secret livré. Aucun déploiement distant ni test Discord de production effectué.
