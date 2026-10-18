# Marchand et taverne intégrés

Le marchand lynx ouvre maintenant son accueil illustré : Histoire, Acheter, Vendre et Partir. Les achats, ventes et objets d’histoire utilisent les nouveaux éléments graphiques du marchand. Quatre emplacements par page ; prix, stock, statut SOLD OUT et chapitres proviennent toujours du serveur. Les confirmations et la quantité de vente sont interactives. Modifier la quantité met à jour le total sans remplacer le champ actif.

La taverne utilise la scène validée avec la panthère au comptoir, le lion troubadour et le loup/renard aux jeux. Les accès aux trois PNJ et au hub sont reliés. Le tavernier présente les six boissons réellement définies, avec les déblocages et délais existants. La table des jeux donne accès aux dés, pile ou face et pierre-feuille-ciseaux existants. Le livre interactif du troubadour est conservé ; son décor utilise désormais le lion validé.

Les fonds sont distincts des données et contrôles natifs. Le fond du comptoir de commerce a été nettoyé avec l’outil de génération intégré : supprimer uniquement titres, onglets, cartes, objets et boutons de la maquette Acheter, préserver le lynx à gauche, la structure du panneau et l’éclairage. Les autres images proviennent des assets validés.

Validation : TypeScript/Vite, 111 tests frontend/DOM, 13 tests ciblés économie et sauvegarde. 52 contrôles navigateur réels sur 1440×900, 1186×570, 390×844 et 320×568 : achat et solde, SOLD OUT, vente de deux ressources, objets par chapitre, retours, six boissons, commande/délai, accès jeu et chapitre du livre. Aucune erreur JavaScript sur ce parcours. Inspection des captures internes PC/mobile. Compilation Python vérifiée.

Limites : aucun accès à la base de production ou au client Discord de production. Le Gold partagé sur PostgreSQL n’a pas été testé en production. Aucun changement des modules serveur, migrations, prix d’outils, récompenses de tutoriel ou données sauvegardées. Les autres menus ne sont pas refondus par cette livraison.

Installation : copier le correctif à la racine du dépôt, envoyer les modifications sur GitHub puis redéployer Coolify. La compilation de production doit être refaite ; copier seulement des images ne suffit pas.
