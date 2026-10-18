# Panneau administrateur Activity

## Accès autorisés
- Moi : 666805849011912705
- Panda : 342359563791761410
- Smogo : 587578557027450900

Les trois identifiants sont comparés comme des chaînes exactes à l’identité Discord vérifiée par le serveur OAuth. Le pseudo, les champs envoyés par le navigateur et les rôles du serveur Discord ne donnent aucun accès. La variable serveur facultative ACTIVITY_ADMIN_IDS remplace la liste par une liste d’identifiants séparés par des virgules. Une valeur vide désactive tous les accès. Aucun réglage frontend ne permet d’accorder une permission.

Le snapshot expose seulement un booléen admin. Le bouton Admin apparaît sur le socle de la statue au centre du hub pour les comptes autorisés. La route privée /api/admin recontrôle la permission à chaque requête, applique le contrôle de requête même origine existant et répond sans cache. Le proxy d’avatars d’autres joueurs est réservé aux administrateurs autorisés. Le menu se ferme à la prochaine actualisation si la permission est retirée ; toute nouvelle action est refusée immédiatement côté serveur.

## Fonctions livrées
- Registre des comptes Discord uniques ayant terminé le tutoriel et dont la récompense est enregistrée, sans import de la liste des membres du serveur Discord.
- Recherche par nom du personnage, pseudo Discord, nom d’affichage ou identifiant exact/partiel. Quatre joueurs par page, recherche temporisée et pagination ; pas de menu déroulant.
- Fiche : niveau, XP, portefeuille, banque et date de récupération du tutoriel. Avatars Discord lorsque le CDN est accessible ; initiale en cas d’indisponibilité.
- Ajout ou retrait de Gold du portefeuille ou de la banque. Ajout d’XP avec synchronisation du niveau. Les soldes ne deviennent pas négatifs ; la baisse d’XP n’est pas proposée pour éviter les incohérences de récompenses de niveau.
- Motif et confirmation obligatoires ; contrôle du solde actuel, clé de requête unique, modification et historique dans une même transaction. Une réponse perdue peut être réessayée avec la même référence sans doubler le versement.
- Historique privé des 30 dernières modifications du joueur : identifiant de l’admin, date, champ, avant/après et motif.
- Consultation de l’inventaire (histoire séparée et marquée), équipement, réputations et délais. Ces quatre catégories sont consultables dans cette livraison ; leur modification et les commandes globales Monde ne sont pas encore implémentées. Aucun faux bouton Monde n’est ajouté.
- Interface avec les assets interactifs existants, boutons centrés, titre et navigation visibles, contenu défilant ; PC, fenêtre Discord basse et mobile.

Le registre et les fiches sont calculés à la demande. Le bouton Actualiser recharge la liste et la fiche sélectionnée, et les modifications rechargent la fiche. Les autres données du jeu conservent leur actualisation périodique habituelle.

## Vérifications locales
Compilation TypeScript/Vite et compilation Python API réussies. 45 tests frontend, 62 tests API dont 11 tests admin : liste exacte, identité anonyme ou forgée refusée, révocation, joueurs éligibles, doublons, recherche et pagination, CSRF, transaction concurrente idempotente, soldes obsolètes, banque, rollback XP et historique.

161 contrôles navigateur : 38 pour l’admin sur PC 1440×900, fenêtre 1186×570 et mobile 390×844 ; 24 pour le tutoriel ; 99 pour les menus et assets existants. Contrôle visuel des captures PC/mobile et ajustement du défilement. CRC des archives et compilation du projet après extraction. Les bases et profils de test sont temporaires ; aucun test ne touche aux comptes ou soldes de production.

## Limites
L’adaptateur conserve son économie SQLite isolée et refuse ECONOMY_DATABASE_URL. Ni la base Gold commune Oddium/PostgreSQL, ni les permissions et avatars de vrais comptes Discord, ni le déploiement Coolify n’ont été vérifiés en production. Les simulations utilisent des identités de test injectées directement dans une base temporaire. Aucun accès de test ou raccourci d’authentification n’est ajouté au serveur livré.

Les illustrations de prévisualisation restent des références visuelles ; le panneau livré est composé en HTML interactif avec les assets existants. Les autres menus et le bot ne sont pas modifiés. Les audits tutoriel présents dans l’archive documentent leurs livraisons précédentes.
