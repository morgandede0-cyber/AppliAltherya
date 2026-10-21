# Blackjack : table interactive

Le modèle validé est intégré dans le jeu réel, sur une base inchangée pour les autres menus et jeux.

## Assets
- `public/assets/blackjack/table-clean.png` : décor sans données ni cartes figées, croupier panthère et sabot conservés.
- `controls-atlas.png` : bois et métal vieilli, cinq jetons détourés par masques vectoriels, découpes SVG indépendantes partageant une seule texture.
- `cards/` : 52 cartes SVG déterministes et un dos. Valeurs, couleurs et nombres de symboles correspondent aux cartes du serveur.

Les deux textures ont été créées avec le générateur d’images intégré : suppression des seules données du modèle de blackjack validé pour le décor ; création d’une plaque vierge en bois et de cinq jetons ivoire, rouge, bleu, vert et noir pour les commandes. Les masques, textes, cartes et interfaces sont du code natif. Aucun solde n’est peint dans le décor.

## Partie
Distribution alternée joueur/croupier depuis le sabot. Carte du croupier cachée pendant le tour du joueur. Tirage progressif et retournement de cette carte à la résolution. Animation des jetons avant affichage du résultat. Actions verrouillées pendant chaque requête et animation. Une partie active se reprend après retour dans la salle.

Mises et résultats calculés côté serveur. Doubler : uniquement avec deux cartes, une mise supplémentaire prélevée une seule fois, une seule carte supplémentaire, puis résolution. Plafond et solde contrôlés sur le serveur. Le montant total de la session est mis à jour pour les remboursements techniques et les statistiques. Le joueur peut tirer ou rester. Pas de partage ni d’assurance dans cette variante ; règle annoncée dans le jeu. Le croupier reste sur 17 souple. Le paiement naturel existant est conservé, avec arrondi au Gold entier.

Commandes accessibles au clavier, dialogue des règles avec focus, variante portrait et animations courtes si la réduction des mouvements est demandée. Le personnage et le décor ne sont pas animés ; les cartes, leur révélation et le règlement des jetons le sont.

## Installation
Remplacer les fichiers de la mise à jour dans le projet, envoyer sur GitHub puis reconstruire/redéployer avec Coolify. Aucun nouveau secret, aucune migration manuelle ni modification du port. Ne pas supprimer la base de données. Les gains et soldes existants sont conservés.
