# Roulette européenne interactive

## Design et assets
Le décor validé avec croupier loup est conservé. Trois assets indépendants ont été créés : `assets/roulette/table-clean.png` (décor vierge), `wheel-bowl.png` (cuve) et `rotor-wood.png` (plateau et croisillon). Les jetons et plaques réutilisent la texture du blackjack, avec découpes SVG transparentes. Les images ont été créées avec le générateur d’images intégré : nettoyage du décor validé et création de deux pièces de roulette vues de dessus, sans chiffres. Les 37 numéros, couleurs, poches, tapis et bille sont tracés en code pour garantir leur exactitude.

## Jouer
Choisir un jeton de 1, 5, 10, 25 ou 50 Gold puis cliquer sur le tapis. Les clics ajoutent les jetons, sans débit avant le lancement. Plusieurs mises sont possibles sur le même tour. Annuler retire la dernière opération ; Effacer vide le tapis. Reprendre les mises recharge les placements du dernier tour sans les engager immédiatement.

Mises proposées : numéro, rouge/noir, pair/impair, 1–18/19–36, trois douzaines, trois colonnes. À cheval : choisir deux numéros voisins. Transversale : choisir une ligne. Carré : choisir son premier numéro en haut à gauche. Sixain : choisir la première des deux lignes. Les mises entre numéros sont représentées sur leur séparation, sans dupliquer les jetons dans toutes les cases couvertes.

Le zéro est vert et unique. Aucune mise extérieure ne couvre zéro. Retours incluant la mise : numéro ×36, à cheval ×18, transversale ×12, carré ×9, sixain ×6, douzaine/colonne ×3, chances simples ×2. Variante sans partage ni prison. Le serveur valide chaque combinaison et le total avant tout débit, prélève une seule mise globale et règle une seule fois la somme des retours gagnants. Le plafond existant s’applique au total. Les multiplicateurs d’événement existants restent appliqués par le moteur du casino.

## Animations et affichage
La roue et la bille tournent en sens opposés, ralentissent, puis la bille descend et rebondit légèrement avant de se stabiliser dans la poche calculée par le serveur. La trajectoire est une animation contrôlée ; ce n’est pas une simulation physique libre qui choisirait elle-même le résultat. Les contrôles et Échap sont bloqués pendant le tour. Le résultat et le règlement des jetons n’apparaissent qu’en fin d’animation. Un rechargement affiche le tour déjà réglé sans le rejouer.

Sur PC : roue à gauche et tapis classique horizontal à droite. Dans une fenêtre Discord haute : roue proportionnée au-dessus du tapis complet. Sur petit mobile : onglets Roue / Tapis de mises, trois pages de douze numéros avec zéro toujours présent, onglets pour les chances simples et les douzaines/colonnes. Les numéros ont des zones tactiles de 44 pixels de haut. Les mises et le premier numéro sélectionné pour une mise à cheval sont conservés en changeant de page ou de vue. Le lancer revient automatiquement à la roue. Le redimensionnement conserve les mises. Réduction des mouvements prise en compte. Le personnage et le décor restent fixes.

## Déploiement
La mise à jour séparée s’applique à la version contenant le blackjack validé. Sinon utiliser l’archive complète. Copier les fichiers dans le projet puis envoyer sur GitHub et reconstruire/redéployer dans Coolify. Aucune nouvelle variable ni migration manuelle. Ne pas supprimer la base. Les requêtes de roulette de l’ancienne interface restent acceptées. Correction incluse pour la touche Échap du blackjack : fermeture des règles seule, et aucune interruption pendant une action.
