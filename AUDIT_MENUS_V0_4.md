# Audit des menus — V0.4

## Réalisé

Cadre buy_slots(2).webp intégré comme habillage réel de la boutique, sans modifier le fichier de référence. Achat, vente et objets d’histoire rendus par un composant interactif commun : catégories, pages, sélection, illustrations SVG, description, prix, stock, quantité, confirmation, état de transaction et résultat serveur.

L’achat d’un objet possédé est bloqué et affiché SOLD OUT. Un solde insuffisant bloque l’achat. La vente filtre les ressources vendables et respecte les stocks. Les objets d’histoire gardent leurs prix et achats du moteur original. Aucune valeur Gold, aucun prix ni récompense ne sont envoyés par le menu au serveur : uniquement l’identifiant de l’action/objet et la quantité éventuelle.

Les doubles clics sont bloqués pendant une transaction. Une ancienne réponse d’actualisation ne peut plus écraser le résultat d’une transaction récente. Les erreurs restent visibles dans le menu et déclenchent une relecture de l’état sans répéter la transaction. La saisie de quantité reste intacte lors de l’actualisation périodique. Les menus historiques achat/vente sous forme de listes sont retirés. Partir revient au hub.

Accès clavier : onglets, sélection et actions ; flèches pour les pages ; Tab reste dans le menu et Échap annule/ferme. CSS spécifique mobile portrait, cartes défilables, boutons −/+ et Tout. Décors et fonctionnalités V0.3 conservés.

## Vérifications

Compilation de tous les modules Python API/bot : réussie. TypeScript et build Vite : réussis. 19 tests TypeScript passent, dont six nouveaux tests des catalogues, catégories, quantités, pagination, requêtes et blocages. 14 tests Python passent, dont un nouveau test de vente exacte/refus de survente/épuisement du stock. Les tests de banque, expéditions, contrats, histoire, cookie et récompenses quotidiennes restent valides.

Les anciens tests TypeScript de combat et sauvegarde locale portent sur les sources historiques conservées. Les nouveaux tests du menu valident sa logique de commerce, pas un rendu visuel ou un clic dans un véritable navigateur.

## Limites

Le navigateur Chromium de test n’a pas pu être installé : le téléchargement reçu est tronqué. Aucun test visuel Brave/PC/mobile, aucun test Activity Discord intégré effectué. Les styles adaptés et les contrôles sont implémentés, mais leur rendu sur les appareils de l’utilisateur reste à vérifier.

Économie de test séparée : aucun accès à PostgreSQL/Oddium ; protection refusant ECONOMY_DATABASE_URL conservée. Le compte Discord n’est pas encore relié à la sauvegarde du navigateur. Aucune mise en production. Les fonctionnalités encore absentes en V0.3 restent décrites dans README.md.

## Correctif V0.4.1

Objets d’histoire retirés des rayons d’achat ordinaires ; collection uniquement via Histoire. Pagination passée à quatre objets, cartes réduites pour quatre emplacements. Test dédié avec neuf objets : pages de 4, 4 et 1, sans perte. Assets des boutons exacts attendus de l’utilisateur ; leur reproduction fidèle reste à réaliser.
