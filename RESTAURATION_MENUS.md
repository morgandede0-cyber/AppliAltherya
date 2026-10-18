# Restauration des menus d’origine

Les images approuvées des dossiers assets/menus, assets/ui et assets/catalog sont à nouveau utilisées. Les zones cliquables sont placées sur les boutons dessinés. Les informations variables remplacent les exemples imprimés dans les images.

Menus concernés : banque, forge, marché (achats, ventes et histoire), tavernier, taverne, jeux, salle clandestine, château, tableau de bord, podium, arène, combat, techniques, ruelle, voleur, braqueur, vigile et préparation/suivi des expéditions.

Les jeux restent animés et interactifs. Le profil, la carte d’Elyndor et le livre du troubadour conservent leur fonctionnement.

## Installation

Copiez le contenu du dossier Altherya_V0_8_10 dans votre projet existant, puis lancez votre fichier de mise à jour GitHub et redéployez dans Coolify. Ne remplacez pas votre base de données ni votre fichier .env. Gardez vos variables Coolify et votre volume de données actuels.

Le petit correctif contient seulement les fichiers modifiés : extrayez-le à la racine du projet, au même niveau que Dockerfile et le dossier apps, puis acceptez le remplacement des fichiers.

## Vérifications

Compilation de production réussie. 34 tests TypeScript et 36 tests Python réussis. Contrôle en navigateur des menus et de leur navigation, dépôt et retrait avec vérification des montants serveur, achat d’un outil, contrôle des limites horizontales sur téléphone. Vérifications réalisées avec des bases de test séparées.
