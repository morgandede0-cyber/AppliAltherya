# Audit V0.5 — assets et hub vierge

## Corrections

Hub : image hub(1).webp fournie, proportions 1672×941 conservées. Onze boutons de l’archive asset.zip affichés comme images dans de véritables boutons : Taverne, Forge, Château, Arène, Marché, Banque, Petites annonces, Ruelle sombre, Panneau central, Monde, Mon profil. Zones et boutons liés au même rectangle ; trois boutons inférieurs élargis et remontés pour les rendre lisibles.

Marchand : scène fournie et quatre boutons illustrés Histoire/Acheter/Vendre/Partir. Rayons et métiers : assets dédiés. Boutons Acheter et Vendre : images dédiées. Croix et flèches : portions du cadre affichées dans des fenêtres SVG, sans modifier le bitmap. Retours/annulation : bouton Partir avec nom accessible précisant son rôle. Les contrôles numériques −/+/Tout restent en HTML, aucun asset spécifique n’étant fourni pour eux.

Objets d’histoire exclusivement dans Histoire, avec onglet Histoire unique. Boutique normale : outils et sac uniquement. Quatre objets par page conservés. Les règles de transaction du serveur ne changent pas.

Formats : les PNG des boutons sont normalisés en WebP lossless pour alléger le client. Alpha et rendu des pixels sur fonds blanc/noir comparés et identiques. Les WebP déjà corrects sont copiés directement. Les sources de l’utilisateur ne sont pas modifiées. Les anciennes images PNG de sprites et leurs décors, inutilisées par le client courant, ainsi que les copies PNG des nouveaux boutons, sont exclues de la livraison.

## Vérifications réalisées

Compilation TypeScript/Vite réussie. Compilation des modules Python API et bot réussie. 22 tests TypeScript et 14 tests Python réussis : boutons référencés présents, vrai format WebP, hub relié à ses destinations, onglet Histoire distinct, pagination de quatre, transactions et régressions du serveur.

Les vieux tests de combat/sauvegarde locale portent sur les sources historiques ; les tests de commerce et d’assets portent sur la version actuelle.

## Limites

Aucun navigateur de test disponible : contrôle visuel Brave, PC/mobile et Discord intégré non réalisé. Dispositions adaptatives et accès clavier implémentés, sans validation sur appareil. Aucun déploiement. Gold et sauvegarde restent isolés du compte Discord et de PostgreSQL/Oddium. Les fonctions non encore intégrées restent détaillées dans README.md.

L’archive contient un seul état graphique par bouton. Les effets CSS de survol, pression et indisponibilité ne sont pas des variantes fournies par l’utilisateur.
