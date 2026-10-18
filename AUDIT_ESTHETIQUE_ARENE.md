# Affinement du menu de l’arène

La structure et les actions du menu validé sont conservées. Le blason dispose d’une place dédiée ; le titre du champion reprend une typographie médiévale à empattements. Le panneau bleu comporte des ombres et des nuances plus travaillées. Classement, champions vaincus et portefeuille sont présentés dans trois cases de même largeur, sur PC et mobile. La disponibilité du champion est séparée des statistiques.

Le panneau de mise utilise le bois des assets existants. L’unité Gold apparaît près du champ, les choix rapides indiquent leur sélection par un éclat doré et un état accessible aria-pressed. La présentation se compacte dans les fenêtres basses de Discord et respecte la préférence de réduction des animations. Les contrôles restent reliés aux fonctions et aux données existantes.

## Vérifications locales
Compilation TypeScript/Vite et Python réussie. 45 tests frontend et 36 tests API réussis. 18 contrôles navigateur de l’arène et de la ruelle sur PC, fenêtre basse et mobile : données réelles, statistiques de largeur égale, typographie, proportions, mise sélectionnée, mise invalide, portefeuille vide et démarrage du combat. 16 contrôles de régression du placement et des combats. Inspection visuelle du menu de préparation dans les trois formats. Archives contrôlées par CRC et reconstruction depuis le ZIP complet.

Le code API/bot et les assets sont inchangés. Cette livraison concerne la présentation de l’arène. Aucun déploiement ni test de la base Gold partagée en production ; ces vérifications restent à faire sur votre serveur. Les fonctionnalités indisponibles dans la version précédente, dont le duel entre amis, restent dans leur état existant.
