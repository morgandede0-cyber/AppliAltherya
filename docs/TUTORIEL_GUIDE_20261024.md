# Tutoriel illustré — douze étapes

Le nouveau parcours remplace l’ancien composant et ses six pages illustrées / son habillage commun. Trois atlas contiennent les douze scènes validées avec une pose différente du loup par lieu. Les parchemins sont vierges : titres, descriptions, objectifs, progression, récompense et commandes sont rendus par le jeu.

1. Bienvenue à Legacy — visite du château et tableau de bord.
2. Identité — vrai profil et identité Discord.
3. Inventaire — ouverture directe du sac, catégories de ressources et objets d’histoire.
4. Métiers et expéditions — préparation en observation.
5. Marchand — rayons d’achat.
6. Forge — consultation des améliorations.
7. Banque — soldes et services.
8. Histoire — carnet et objectifs à accomplir dans les lieux.
9. Missions — petites annonces et explication des quotidiennes.
10. Combat — arène, techniques et règles des boss de la tour.
11. Monde — carte et conditions des destinations.
12. Fin — récompense unique et première quête principale.

## Interaction et sauvegarde

Le bouton principal ouvre le vrai menu en observation. « Revenir au guide » ramène au parchemin ; le bouton principal devient « Continuer ». Les liens Précédent et Revoir permettent de revenir sur une découverte. La dernière page réclame directement la récompense sans imposer une visite supplémentaire.

Le serveur exige les onze découvertes précédentes, vérifie leur destination, le joueur et l’étape. Il enregistre la dernière page et le paiement dans la même transaction. Gold et XP ne viennent jamais du client. Double clic, requêtes concurrentes et relecture ne donnent pas de nouveau paiement.

Bonus conservé : 100 Gold et 25 XP. Aucun tarif ni objet n’est modifié.

Pour la nouvelle révision obligatoire, tous les joueurs recommencent à l’étape 1, y compris ceux ayant terminé. Les reçus de récompense sont conservés. Les visites précédentes sont effacées lors du changement de révision ; les découvertes du nouveau parcours sont ensuite conservées. La relecture est disponible depuis le profil.

Sur PC : loup à gauche et texte intégré au parchemin à droite. Sur mobile portrait : scène en haut et parchemin lisible dessous, texte défilant si la hauteur est insuffisante. Les boutons restent dans la feuille.

## Assets

`wolf-scenes-1.png`, `wolf-scenes-2.png`, `wolf-scenes-3.png` : planches validées, débarrassées des textes et boutons avec l’outil intégré de génération d’images, en préservant les poses, accessoires, décors et cadres. Prompt : suppression des seuls textes, pictogrammes, chiffres et boutons intérieurs, restitution du papier vierge ; invariants : toutes les scènes et poses validées, éclairage et bordures conservés.

`wolf-button.png` : bouton en bois sombre à extrémités biseautées et bordure dorée fine, sans texte, extrait/recréé depuis le modèle validé avec l’outil intégré, fond transparent. Les libellés sont toujours interactifs.

Les anciens `page-0.png` à `page-5.png` et `guide-skin-v2.png` ne sont plus référencés ni livrés. Aucun ancien menu n’est conservé comme alternative.

## Installation

Archive de mise à jour cumulative : copier son contenu sur le projet existant en remplaçant les fichiers, puis reconstruire/redéployer le frontend et redémarrer l’API. Ne pas remplacer la base de données, les variables d’environnement ou les sauvegardes. La remise à zéro du tutoriel est automatique et unique pour cette révision.

Le prébuild retire automatiquement les anciennes images encore présentes après une copie de mise à jour : uniquement `page-0.png` à `page-5.png` et `guide-skin-v2.png` dans `apps/game/public/assets/tutorial/`.

Les essais sont réalisés avec une base temporaire et de faux profils Discord ; pas de déploiement ni d’accès aux données de production pendant cette livraison.
