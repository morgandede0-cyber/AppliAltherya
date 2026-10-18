# Installer le correctif de connexion Activity

Base : Altherya_Admin_Securise, version 22. Le petit correctif contient seulement les fichiers modifiés et ajoutés ; le ZIP complet contient aussi tous les assets existants.

1. Extrayez le ZIP. Copiez le contenu du dossier Altherya_V0_8_10 dans votre projet actuel, à l’endroit où se trouve déjà le Dockerfile. Acceptez les remplacements. Mettez à jour ensemble l’API et le frontend.
2. Conservez vos .env, ACTIVITY_DB, le volume persistant et les sauvegardes. Ne copiez aucune base de test. Aucune nouvelle variable n’est requise.
3. Envoyez les fichiers sur votre dépôt GitHub puis redéployez dans Coolify. Le Dockerfile reconstruit le frontend ; un simple redémarrage de l’ancien conteneur ne suffit pas.
4. Gardez DISCORD_CLIENT_ID=1529936499775242250 au Runtime, VITE_DISCORD_CLIENT_ID=1529936499775242250 au Buildtime, et votre vrai DISCORD_CLIENT_SECRET uniquement au Runtime. Le correctif ne contient aucun secret. Conservez PORT et ACTIVITY_DB actuels.
5. Fermez complètement l’Activity Discord et relancez-la depuis Discord. Vérifiez que votre personnage apparaît, que le tutoriel s’ouvre si nécessaire puis que votre progression reste après une nouvelle ouverture. Si une erreur persiste, le nouveau message indiquera l’étape et le détail à transmettre sans exposer de secret.

Le mapping / → altherya.magicgg.fr et les réglages Discord déjà saisis restent inchangés. La liste admin reste limitée aux trois identifiants demandés. Aucun déploiement n’est effectué automatiquement par cette archive.
