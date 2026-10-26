# Correctif mobile — 27 octobre 2026

## Corrections
- La zone vide autour du suivi de quête ne capte plus les appuis sur les autres boutons de la scène. Les boutons de quête restent interactifs.
- Sur écran étroit ou paysage de faible hauteur, la scène derrière les menus illustrés du marchand, de la taverne et des panneaux studio est masquée pendant l'ouverture du menu, afin d'éviter la superposition de deux décors. Elle réapparaît à la fermeture.
- Le retour d'un service depuis le marché réaffiche le marchand.
- Sur petits écrans, les cartes du marchand laissent plus de place aux noms et aux usages des objets, la pagination ne chevauche plus l'ornement et le portefeuille et le bouton de retour sont réduits. Les 4 objets par page et les prix sont conservés.
- Le panneau central contient une entrée pour ces corrections.

## Vérifications
- Construction TypeScript/Vite et compilation Python réussies. 261 tests d'interface réussis après les corrections.
- Parcours mobile étendu : 132 contrôles sur 4 formats (320, 360, 390 et 414 px), en incluant les principales activités. Les deux premiers formats ont été parcourus avant le dernier ajustement du marchand ; celui-ci a ensuite été retesté sur 3 portraits et un paysage, à 170 % d'agrandissement du texte.
- Tests ciblés : 28 contrôles sur 320×568, 360×780, 390×844 et 844×390, dont appui sur le marché malgré la zone de quête, accès au comptoir des joueurs, achat et retour. Aucune erreur JavaScript observée.
- Accès de quêtes, services directs et journal : 52 contrôles sur 2 PC et 2 téléphones, sans erreur JavaScript ou asset absent détecté. Audit des assets : 220 références, aucune manquante.
- Les 601 tests serveur de la livraison précédente avaient été réussis ; ils n'ont pas été relancés pour cette modification d'interface. Les tests utilisent une base temporaire et ne changent pas les prix, récompenses ou données de production.

## Limites et installation
Ces vérifications sont des simulations locales, pas un test sur le téléphone réel et la version Discord de chaque joueur. La base partagée Oddium et le serveur Coolify de production n'ont pas été testés. Si un écran reste défectueux dans Discord, fournir le lieu, la taille/orientation et une capture permettra de reproduire le cas.

Cette archive est cumulative et doit être appliquée sur le projet existant : copier le contenu du dossier Altherya_V0_8_10 dans le projet, remplacer les fichiers, puis reconstruire et redéployer dans Coolify. Aucun changement de variables d'environnement ou remise à zéro n'est nécessaire.
