# Installation

Le projet complet contient tous les fichiers et assets. Le correctif contient uniquement les fichiers ajoutés ou modifiés depuis la version avec la banque transparente sans coffre (version 15).

1. Sauvegardez votre projet actuel et vos paramètres.
2. Extrayez le dossier Altherya_V0_8_10. Pour le correctif, copiez son contenu dans le même dossier de votre projet et acceptez le remplacement des fichiers.
3. Conservez vos fichiers .env et vos données : ces archives n’en contiennent pas.
4. Publiez les modifications avec votre procédure GitHub habituelle puis redéployez dans Coolify. Le Dockerfile existant construit le jeu.

Pour une compilation locale : dans apps/game, exécutez npm ci puis npm run build. Après déploiement, vérifiez la connexion Discord, les soldes, une transaction et leur conservation après rechargement.
