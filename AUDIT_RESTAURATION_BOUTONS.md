# Audit — retour au placement d’origine

## Correction

Grille portrait en deux colonnes et dock de paysage supprimés. Tous les accès du hub reprennent leurs coordonnées sur le décor, dont Annonces et Ruelle sombre. La scène entière est ajustée proportionnellement à la fenêtre, sans recadrage. Le bouton Admin retrouve son ancrage précédent sur la statue et conserve sa restriction aux ID autorisés.

Le nouvel écran de lancement, son blason transparent et sa progression restent présents. Le bandeau du joueur reste compact. Aucun autre menu ni asset n’a été remplacé.

## Vérification locale

- Compilation TypeScript et build Vite : réussis.
- 55 tests frontend : réussis.
- 27 contrôles Chromium : coordonnées d’origine des onze accès sur cinq formats PC/mobile, proportions complètes du décor, rotation, Banque et Profil, lancement et reprise sur erreur.
- Captures portrait et paysage examinées : accès revenus sur les bâtiments, absence de grille et de dock.
- Modules Python compilés ; régressions API exécutées séparément, résultat final indiqué dans la livraison.
- Comparaison des fichiers API, moteurs de jeu et assets avec l’archive de départ : aucun changement.
- ZIP : intégrité et présence du lanceur, de son blason et des sources vérifiées.

## Limites

Le retour aux proportions d’origine rétablit aussi un décor plus petit dans une fenêtre verticale et des boutons qui se réduisent avec lui, conformément à la demande de retour au placement précédent. Les vérifications mobile utilisent un navigateur avec dimensions simulées ; pas de test sur téléphone physique ou dans une session Discord réelle.

Pas de modification de données ni de configuration serveur. Le stockage économique existant est conservé ; le partage du Gold avec Oddium n’est pas implémenté ni validé par cette correction.
