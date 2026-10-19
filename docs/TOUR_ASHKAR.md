# Ouverture de la Tour d’Ashkar

Accès : Monde → Tour d’Ashkar, niveau 5. Le bouton existant de la carte ouvre désormais un menu jouable, à la place de l’écran d’attente.

L’ascension comprend les dix étages historiques : Rat des Profondeurs, Gobelin Pillard, Squelette Errant, Garde Déchu, Orc des Cavernes, Berserker Orc, Chevalier Corrompu, Golem d’Obsidienne, Exécuteur des Abysses et Varkhaz. Les portraits et le décor sont nouveaux ; les noms et récompenses viennent du système existant. Les PV des gardiens sont désormais exprimés sur l’échelle du moteur de l’arène, fixe pour chaque étage.

## Règles conservées

Trois **nouveaux étages validés** par jour, réinitialisation à minuit à Paris. Une défaite ou un abandon ne consomme pas de validation, ne retire pas de Gold et ne fait pas redescendre. Chaque étage rapporte sa récompense une seule fois. Les valeurs d’origine restent inchangées :

| Étage | Gold | XP | Pouciel |
|---|---:|---:|---:|
| 1 | 10 | 15 | 0 |
| 2 | 15 | 18 | 0 |
| 3 | 20 | 21 | 0 |
| 4 | 25 | 24 | 0 |
| 5 | 30 | 28 | 1 |
| 6 | 40 | 32 | 0 |
| 7 | 50 | 36 | 0 |
| 8 | 65 | 40 | 0 |
| 9 | 85 | 45 | 0 |
| 10 | 120 | 75 | 3 |

Les Pouciels arrivent dans le même `legacy_wallet` que celui utilisé à KHAZ’GORAM. Les dix premières validations offrent quatre Pouciels au total. Les revanches restent jouables pour apprendre une technique, avec zéro Gold, XP et Pouciel. Aucun tarif d’équipement ou bonus de tutoriel n’a été modifié.

## Combats et interface

Les techniques communes progressent avec le niveau, sans choix de classe. Chaque gardien vaincu donne une technique unique, conservée dans le même grimoire que les techniques de champions. Le remplacement est gratuit et limité au même emplacement. Les dégâts, esquives, gardes, recharges et effets des techniques utilisent désormais le même moteur `arena_combat` / `arena_techniques` / `arena_engine` que l’arène. La tour réutilise aussi son écran de combat et son grimoire. Le module Discord historique n’est pas importé. Les bonus d’équipement sont fixés au début du combat.

Le menu propose la préparation, les dix étages en pages de quatre, le combat avec PV et journal, puis le résultat. Le nom et la photo serveur sont repris quand l’identité Discord est disponible ; le mode local utilise un portrait neutre. Les barres et nouvelles lignes du journal sont animées et respectent la réduction des mouvements. Mobile : attaques sur deux colonnes, cadre défilant, résultat compact.

Un combat en cours reprend après actualisation, reconnexion ou redémarrage. Revenir sur la carte ne l’abandonne pas. Le joueur peut ensuite revenir dans la tour ; pour lancer un autre combat ou changer son équipement, il doit terminer ou abandonner celui-ci. Une seule activité de combat/jeu peut être lancée en parallèle de la tour.

## Sauvegarde et événements

Les tables historiques `ashkar_progress`, `ashkar_daily`, `legacy_equipment` et `legacy_wallet` sont conservées. Les nouveaux états et reçus utilisent `activity_ashkar` et `activity_ashkar_receipts`. La victoire met à jour atomiquement la progression, le quota, le Gold, l’XP, le Pouciel et le reçu. Révisions strictes et reçus uniques protègent les confirmations répétées et les requêtes concurrentes. Aucune remise à zéro des joueurs.

Les événements de début/fin et les gains alimentent la file de logs Discord existante. Le dixième étage envoie un événement Hall de Gloire. La diffusion réelle dépend du bot et des permissions déjà configurés ; aucun message réel n’a été envoyé pendant les tests.

## Assets et installation

Deux images générées avec l’outil intégré : `apps/game/public/assets/ashkar/hall.png` et `enemies.png` (dix portraits). Les régions de l’atlas sont définies dans `ashkar-art.json`, les prompts dans `ashkar-generation.json`. Le menu réutilise les boutons et cadres de KHAZ’GORAM.

La mise à jour s’applique au projet avec les derniers menus de KHAZ’GORAM. Le ZIP complet contient les deux fonctionnalités. Sauvegarder la base existante, copier les fichiers et redéployer via la procédure habituelle. Les schémas se créent automatiquement. La dépendance `tzdata` garantit le calendrier Paris dans les conteneurs sans données système de fuseau horaire. Aucun `.env` ni fichier de données de joueurs n’est livré. Aucun déploiement distant n’a été réalisé.

## Vérifications

269 tests serveur réussis (suite complète). Compilation Python de l’API et du bot ; compilation TypeScript et build Vite ; 160 tests client réussis, dont trois tests de menu Ashkar. Dix tests serveur Ashkar couvrent accès, étage interdit, riposte, recharge, sauvegarde, récompense, Pouciel partagé, trois validations/jour, passage au lendemain, perte/repli, concurrence, rollback, boss final et conservation d’une progression historique.

Parcours navigateur avec API réelle locale et base temporaire : ordinateur 1440×900 et mobile 390×844 ; accès par la carte, atlas, combat, défense, reprise après rechargement, victoire, paiement exact, continuation à l’étage suivant et abandon. Les victoires de vérification accélèrent uniquement les PV de l’ennemi dans cette base temporaire. Captures inspectées ; aucun débordement horizontal ou erreur de chargement.

Limites : récompenses historiques conservées ; la tour ne dépasse pas dix étages. L’équilibrage de combat utilise maintenant l’échelle de l’arène ; les PV fixes d’étage sont les anciens PV divisés par six, arrondis, sans adaptation au niveau du joueur. Production, session Discord réelle et connexion au serveur Oddium non testées ; aucune infrastructure d’économie n’a été modifiée.
