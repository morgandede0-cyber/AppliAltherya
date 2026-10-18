# Audit — menu illustré du portail Discord V2

## Livraison réelle

Le projet contient le visuel complet approuvé dans apps/game/public/assets/discord/portal-altherya.png (PNG RGB 1672×941), inchangé. Le bot publie une Media Gallery avec une seule image entière, puis une ligne avec le vrai bouton natif Jouer à Altherya dans un même Container V2. Le panneau n’est plus un embed textuel ni une maquette d’interface. L’accès peint dans le dessin n’est pas cliquable ; le bouton Discord placé dessous est l’accès fonctionnel.

La conversion d’un portail V1 existant garde son ID et son custom_id. Les anciens champs content, embeds et attachments sont explicitement vidés lors de l’édition par LayoutView. Les nouveaux messages utilisent IS_COMPONENTS_V2 (32768), sans champs content ou embeds. La détection d’un portail parcourt maintenant les composants imbriqués pour reconnaître aussi bien les messages V1 que V2.

L’image est accessible sur le domaine public existant et copiée dans dist par le build Vite/Docker. Une URL avec hash du contenu renouvelle le cache lors d’un changement d’image. ALTHERYA_PUBLIC_URL permet un autre domaine HTTPS ; les identifiants dans l’URL et les URL non HTTPS sont refusés.

## Vérifications

- Compilation de tous les modules Python API et moteurs bot : réussie. Revue des nouveaux imports et suppression du générateur d’embed devenu inutilisé.
- **130 tests API réussis**, dont **36 tests portail/restauration**. Les nouveaux cas vérifient une image unique suivie du bouton, l’absence de content/embeds dans une création V2, la migration sans nouvelle publication, la reconnaissance imbriquée, la validation de l’URL publique et le callback réel du bouton.
- La vraie méthode discord.py Message.edit est exécutée avec transport HTTP simulé : le payload généré porte IS_COMPONENTS_V2 et vide correctement les champs V1. La méthode de lancement native génère toujours type 12. Les appels au serveur Discord réel restent simulés.
- Un message V2 réellement décodé par discord.py depuis le payload est reconnu comme notre portail (pas seulement des objets de test simplifiés).
- Service HTTP local : image servie sans session avec HTTP 200, Content-Type image/png, paramètres de révision acceptés et contenu identique au PNG source.
- Build TypeScript/Vite et **47 tests frontend** : réussis. Le PNG du portail existe bien dans le build.
- **24 contrôles navigateur tutoriel**, sans erreur JavaScript, sur PC 1440×900, fenêtre courte 1186×570 et mobile 390×844. L’interface du jeu n’est pas modifiée ; le panneau Discord lui-même doit encore être vérifié dans le client Discord après déploiement.
- ZIP complets/correctif : CRC vérifié, image et fichier règles présents ; reconstruction du projet depuis le ZIP complet extrait réussie.

## Changements limités

Par rapport à la version Portail Discord précédente : discord_portal.py, son test et la documentation d’installation sont mis à jour ; le visuel du portail et ce rapport sont ajoutés. Les assets existants, menus du jeu, moteurs économiques, tutoriel et whitelist admin sont conservés. Pas de changement de port ni de réinitialisation de données. Le fichier règles source restauré dans la version précédente est conservé dans l’archive complète.

## Points à vérifier sur le serveur

Aucun accès authentifié au Coolify ou au bot réel : aucun message Discord réel n’a été modifié ici. Mettre les fichiers dans GitHub et reconstruire/redéployer le service Activity avec son token existant. Vérifier que Discord peut lire l’image publique et que le bouton ouvre bien l’Activity.

Le bouton garde le style, l’alignement et les dimensions imposés par Discord. Aucun bouton sur toute la largeur, superposé à l’image ou zone cliquable cachée n’est simulé. Le message V2 ne peut pas être reconverti en V1 sur le même ID ; la procédure de retour est documentée. La déduplication conserve les limites décrites dans l’audit du portail précédent.

L’économie reste la SQLite isolée de l’Activity ; le Gold partagé Oddium/PostgreSQL n’est pas validé en production par cette livraison. Les logs/Gazette et l’utilitaire explicite de restauration du point d’entrée sont conservés.
