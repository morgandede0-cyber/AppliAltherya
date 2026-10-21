# Roulette : correction de la disposition

## Problème corrigé

Le mode portrait imposait un plateau de 1 500 px et une roue de hauteur fixe de 210 px. Une fenêtre Discord haute, même large, recevait donc un affichage de téléphone : roue trop aplatie, tapis vertical interminable et commandes fixées sur les dernières cases.

## Nouvelle disposition

- Fenêtre PC large : roue à gauche, tapis classique horizontal à droite. Le zéro est unique ; les 36 autres numéros sont placés sur trois rangées.
- Fenêtre Discord haute ou tablette : roue proportionnée au-dessus du tapis complet, croupier visible, commandes dans le flux.
- Petit mobile (moins de 700 px) : onglets Roue / Tapis de mises ; trois pages de douze numéros avec zéro toujours présent ; chances simples et douzaines/colonnes dans leurs onglets. Les numéros font 44 px de haut. Les mises restent en place en changeant de page, de vue ou de taille de fenêtre. Une mise à cheval peut traverser deux pages.
- Le lancement affiche automatiquement la roue sur petit écran et verrouille toutes les commandes. Les jetons de mises combinées suivent les nouvelles séparations du tapis.

Le décor, le croupier, la cuve et le rotor approuvés sont conservés. Aucun nouvel asset bitmap n’est créé pour ce correctif. Le problème provenait du placement et des dimensions. Les règles, probabilités, plafonds, versements et monnaies restent inchangés. Un résultat déjà réglé n’est plus réutilisé comme nouveau résultat en cas d’échec d’une demande.

## Installation

Appliquer les fichiers de ce correctif sur la version complète contenant les huit jeux. Le dossier Altherya_V0_8_10 contient la racine du projet : copier son contenu, envoyer sur GitHub puis reconstruire/redéployer via Coolify. En cas de doute sur les versions précédentes, utiliser le ZIP complet. Ne pas supprimer la base de données ou les variables d’environnement. Aucun déploiement distant n’est effectué par cette livraison.

## Audit

- Construction TypeScript / Vite réussie. Compilation syntaxique de 90 modules Python réussie.
- 147 tests de l’interface réussis, dont nouveaux contrôles de placement des mises combinées, mises à cheval entre pages, conservation des mises en changeant de vue/groupe/page et verrouillage des onglets pendant une manche.
- 5 tests serveur roulette réussis, incluant les gains pour les 37 numéros et la validation des mises. Les fichiers de production API et moteurs restent identiques à l’archive précédente ; la suite serveur complète n’a pas été relancée.
- Parcours navigateur avec API réelle et base temporaire : 1440×900, 1186×570, 806×1110, 800×900, 390×844, 320×568. Contrôle de la proportion de roue, de l’ordre des cases, des pages et des zones tactiles, de l’ajout/annulation des mises, du verrouillage, de la rotation effective, de la bille finale, des gains serveur et du portefeuille, des règles et du retour à la salle clandestine. Aucun asset manquant ni erreur de navigateur sur les parcours réussis.
- Après finition visuelle, nouveau parcours PC, fenêtre 806×1110 et mobile 390×844 ; contrôle supplémentaire du passage 806→390→806 sans perdre les mises.
- Inspection visuelle des captures locales PC, de la fenêtre haute correspondant à la capture signalée et des deux vues sur mobile. Les tests sont réalisés en navigateur local, pas dans le client Discord ni sur les données Gold/Oddium de production.
- Archives contrôlées par CRC ; toutes les entrées non concernées sont conservées, notamment les autres jeux et la correction de la main du renard.

Les trajectoires restent les animations de présentation existantes, pilotées par le résultat serveur ; elles ne constituent pas une simulation physique libre.
