# Tutoriel illustré, nom Discord et nouveau passage obligatoire

## Design intégré
Les six PNG validés dans la conversation sont maintenant intégrés dans apps/game/public/assets/tutorial/page-0.png à page-5.png, sans redessin ni altération. Ils comprennent le garde bleu et or, les encadrements, les illustrations, les textes et les boutons d’origine. Les anciens panneaux génériques du tutoriel sont remplacés.

Les contrôles Précédent, Continuer, Commencer et Entrer sont de vrais boutons HTML accessibles et alignés sur les éléments graphiques correspondants. Les requêtes passent par l’API ; les images ne décident ni de la progression ni du paiement. La touche Échap ne ferme pas le parcours obligatoire. La relecture volontaire reste accessible depuis le profil.

Sur PC, le visuel complet reste proportionné et centré. Sur mobile, l’illustration accompagne une transcription lisible avec défilement ; les mêmes boutons graphiques restent accessibles en bas. Il n’y a pas de fond gris ajouté et les transparences d’origine sont conservées. Les montants peints correspondent à la règle de bienvenue (100 Gold et 25 XP), pas au solde du joueur. Le statut réel de récupération provient du serveur et précise quand aucun nouveau gain n’est possible.

## Nom automatique
Le formulaire de choix du nom a été supprimé du démarrage. Après OAuth, le serveur utilise global_name de Discord, avec username en secours. Chaque nouvelle connexion synchronise les noms de toutes les sessions rattachées au compte ; aucune saisie frontend ne permet de changer le nom d’un profil Discord vérifié. Les noms sont insérés avec textContent. L’identifiant Discord reste la clé d’identité, donc un changement de pseudo ne crée pas un nouveau joueur ni une nouvelle récompense.

Le surnom spécifique d’un serveur Discord n’est pas récupéré : cette version utilise le nom d’affichage du compte obtenu avec le scope identify déjà en place.

## Remise à zéro du parcours
La nouvelle révision illustrated-20261015-v1 invalide les validations de l’ancien tutoriel. Au premier état chargé après déploiement, chaque profil revient à l’accueil et doit terminer le nouveau parcours. Sa progression dans ce nouveau parcours est ensuite conservée : les actualisations et redémarrages ne le remettent pas à zéro une deuxième fois.

Le registre admin ne liste que les validations de la révision actuelle ; les joueurs y réapparaissent à mesure qu’ils terminent. Les preuves de récompense antérieures restent conservées dans activity_tutorial_receipts et tutorial_progress. Un joueur déjà récompensé refait donc le guide sans recevoir 100 Gold ou 25 XP supplémentaires. Les soldes, inventaires, historique et autorisations admin sont conservés. Il n’y a aucune suppression globale de la base de données.

## Vérifications locales
Compilation TypeScript/Vite, compilation Python API, 47 tests frontend et 76 tests API réussis. Les sept nouveaux tests couvrent le nom automatique et son changement sur plusieurs appareils, le secours username, le refus du renommage manuel, le nouveau parcours obligatoire sans double récompense, la reprise après redémarrage, le registre admin de la révision et le bouton Précédent.

170 contrôles navigateur : 24 tutoriel sur PC, fenêtre Discord basse et mobile, incluant absence du formulaire, retour à l’étape précédente, reprise, erreur réseau, récompense, banque et relecture ; 38 admin ; 99 menus et assets ; 9 connexion en iframe HTTPS avec cookie partitionné. Les zones graphiques des boutons sont vérifiées sur leurs surfaces cliquables ; les captures PC/mobile ont été inspectées. CRC des ZIP, comparaison binaire des six PNG avec les références et reconstruction du projet extrait.

Les tests utilisent des bases temporaires et des identités simulées. Aucun compte réel, aucune donnée Coolify et aucune base de production n’ont été modifiés. Les correctifs de cookies et les trois comptes admin autorisés restent en place. L’économie conserve l’adaptateur SQLite isolé ; l’économie PostgreSQL/Oddium et le lancement réel sur votre serveur restent à vérifier après déploiement. Les audits plus anciens décrivent leurs livraisons respectives ; ce document décrit le tutoriel désormais intégré.
