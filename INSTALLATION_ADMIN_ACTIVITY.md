# Installation du panneau Admin

Ce correctif s’applique à Altherya_Tutoriel_Obligatoire (version 21). Copiez le contenu de Altherya_V0_8_10 dans le projet et acceptez les remplacements. Mettez à jour ensemble l’API et le frontend. Le projet complet contient tous les assets existants ; le petit correctif contient seulement les fichiers ajoutés ou modifiés.

Conservez votre configuration Discord, vos fichiers .env et la base ACTIVITY_DB sur un volume persistant. Sauvegardez la base avant le redéploiement. La table d’historique admin est créée automatiquement au démarrage. Aucune nouvelle variable n’est nécessaire pour les trois comptes demandés. Si ACTIVITY_ADMIN_IDS est déjà défini, son contenu remplace la liste intégrée : mettez-y 666805849011912705,342359563791761410,587578557027450900 pour conserver ces trois accès.

Construisez le frontend avec npm ci puis npm run build depuis apps/game, puis redéployez via la procédure GitHub/Coolify existante. Dans Discord, reconnectez un des trois comptes autorisés : le bouton Admin doit apparaître sur la statue du hub après le tutoriel. Vérifiez qu’un compte ordinaire ne le voit pas. Les identifiants doivent venir de la connexion OAuth Discord ; changer simplement le pseudo ne donne aucun accès.

Le panneau permet pour l’instant la gestion du Gold et l’ajout d’XP, ainsi que la consultation des autres rubriques et de l’historique. Consultez AUDIT_ADMIN_ACTIVITY.md pour le détail des vérifications et des limites. Ce fichier ne constitue pas un déploiement automatique.
