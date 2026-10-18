# Audit — animations discrètes du hub

## Périmètre

Ajout d’un module `hub-life.ts` branché sur le cycle de navigation existant. Il dessine une couche transparente, calée sur les 1672×941 pixels de l’illustration actuelle. Les sources lumineuses et les jets ont été repérés sur l’image et contrôlés en vue agrandie.

Le placement, la taille et les actions des boutons ne changent pas. La couche est décorative (`pointer-events: none`, masquée pour les technologies d’assistance) et reste sous les accès interactifs. Aucun personnage ou bâtiment n’est déplacé. Pas de nouveau menu ni de son automatique.

## Cycle de vie et performances

Un seul propriétaire d’animations par scène. La sortie du hub annule la boucle, débranche les observateurs et retire la couche. Un retour au hub crée une seule nouvelle couche. Pause et effacement lors d’un menu, d’une connexion en cours, d’une transition, d’un onglet masqué ou d’une préférence de mouvement réduit. La reprise conserve une horloge continue sans saut de temps.

Résolution plafonnée à 1,6 million de pixels, densité maximale 1,5 ; dessin limité à 24 ou 30 images par seconde selon la largeur. Un contexte Canvas indisponible laisse le hub statique utilisable.

## Validation

- Compilation TypeScript et build Vite réussis ; imports du nouveau module résolus.
- 59 tests frontend réussis, dont trajectoires de gouttelettes, propriétaires uniques, pause/reprise, mouvement réduit, taille nulle et absence de Canvas.
- Tous les modules Python de l’API et des moteurs compilés ; 156 tests API réussis, sans échec ni erreur.
- 42 contrôles navigateur du hub sur six formats : 1440×900, 1186×570, 809×1110, 390×844, 844×390 et 320×568. Vérification des pixels animés, résolution, alignement, coordonnées d’origine, accès Banque/Profil, rotation, réduction des animations et absence de couche dans les autres lieux.
- 24 contrôles navigateur de tutoriel et 15 contrôles de pseudos serveur/profils/admin réussis.
- Revue visuelle PC/mobile et repérage agrandi de la cheminée, des lanternes et de la fontaine.
- Comparaison avec l’archive précédente : aucun changement de l’image, des assets, des positions de scène, du backend, des moteurs, de la configuration ou des dépendances.
- Intégrité ZIP, présence de `apps/game/src/data/rules.ts` et du nouvel effet vérifiées ; reconstruction du frontend depuis extraction de l’archive complète.

## Limites et données

Les effets sont volontairement localisés et discrets. Ils ne reconstruisent pas la scène en 3D et ne font pas marcher les personnages déjà peints dans l’image. Si la réduction des animations est activée, le décor reste statique.

Les essais navigateur utilisent des dimensions PC/mobile simulées. Le déploiement Coolify, la session Discord réelle et les téléphones physiques ne sont pas accessibles dans cet environnement et restent à vérifier après installation.

Aucune migration, aucune écriture de données de jeu par le module. Les tests économiques existants passent, mais le partage de Gold avec Oddium n’est pas implémenté ni validé dans cette base Activity. La persistance reste celle du stockage existant et du volume installé sur le serveur.
