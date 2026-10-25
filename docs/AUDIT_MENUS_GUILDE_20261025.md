# Validation des menus

- Compilation Vite réussie (avertissement existant de taille de bundle).
- 257 tests de régression réussis, aucun échec.
- Parcours navigateur des menus : 120 contrôles réussis ; aucune erreur JavaScript ni asset manquant.
- Parcours navigateur hotbar, livres et navigation : 120 contrôles réussis.
- Formats testés : 1440 × 900, 1186 × 570, 390 × 844 et 320 × 568.
- Audit des chemins littéraux : 210 références d’assets, aucune manquante.
- Compilation Python de l’API réussie.

Les parcours utilisent une API locale et une base isolée : achat effectif et variation du solde, dépôt/retrait, équipement, boissons et jeux, combat jusqu’au résultat, signature de contrat et affichage du timer. Les autres vérifications couvrent les quatre objets par page, les chapitres, les noms du serveur et la séparation de l’inventaire.

Les images de contrôle sont internes et ne sont pas livrées. Le lancement dans Discord, les photos Discord réelles, le stockage de production et le déploiement Coolify ne sont pas validés par ces tests locaux. Les écrans courts conservent un défilement intérieur.
