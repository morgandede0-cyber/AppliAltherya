# Popie, la contrebandière

Accès : Monde → Port des Brumes → Entrepôts → Comptoir de Popie.
Le port conserve son déblocage par la quête principale S1-Q08. Popie ne modifie ni les indices ni l’avancement de l’enquête.

## Services intégrés

- Commandes : trois demandes quotidiennes portant sur Pierre brute, Bois de chêne ou Viande de sanglier. Une seule peut être honorée par journée de Paris. Quantité : 4 à 7. Paiement : valeur de vente des ressources + 2 Gold, et 3 XP.
- Échanges : trois opérations par jour, chacune remet 3 ressources contre 2 d’un autre matériau de base. Le circuit complet perd des ressources ; il ne permet pas d’en dupliquer. Aucun objet d’histoire, de quête, outil ou équipement n’est accepté.
- Livraisons : un départ par jour. Deux Bois de chêne sont retirés au départ. Trajet sûr : 5 minutes, 100 %, 8 Gold et 4 XP. Trajet risqué : 8 minutes, 70 %, 14 Gold et 6 XP. Un échec perd uniquement les deux ressources confiées, sans autre prélèvement.

Un résultat attend sa récupération même après minuit ou une reconnexion. Une livraison en attente empêche un second départ. Les objets sont consommés dès leur remise, jamais à la récupération du résultat.

## Persistance et contrôle

La table additive `activity_popie` contient l’état personnel et les limites quotidiennes. Les actions utilisent la transaction commune, le journal économique, les reçus de requête et la révision du port. Le résultat aléatoire est fixé par le serveur au départ et masqué jusqu’à sa récupération. Aucun montant, délai ou résultat reçu du client n’est utilisé. La maintenance du port, de la campagne et du jeu s’applique.

Le tutoriel et les tarifs des outils ne changent pas. Les récompenses existantes des quêtes restent inchangées. Aucune nouvelle variable d’environnement n’est nécessaire.

## Présentation

Scène originale du comptoir, panneau vierge et bouton PNG transparent. Les contenus restent de vrais éléments interactifs et accessibles au clavier, avec confirmation avant de retirer des ressources. Trois onglets, compte à rebours en secondes, retour au port et aux entrepôts. Sur mobile le panneau suit la scène ; sur PC il occupe la partie droite.

Assets dans `apps/game/public/assets/popie`. Les consignes de génération sont archivées dans `docs/popie-prompts.json`.

## Déploiement

Mettre à jour le projet et reconstruire l’image avec le processus habituel. Conserver le volume de données et les variables existantes. Aucun serveur de production n’a été modifié pendant cette livraison.
