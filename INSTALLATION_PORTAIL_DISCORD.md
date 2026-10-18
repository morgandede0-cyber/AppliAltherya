# Portail Discord — Altherya

## Mise à jour : menu illustré V2

Le visuel Altherya complet est inclus dans `apps/game/public/assets/discord/portal-altherya.png`. Il est affiché entier dans une Media Gallery, suivi du vrai bouton natif **Jouer à Altherya**, au sein d’un seul Container Components V2. Aucune découpe du décor. Le bouton contenu dans le dessin reste décoratif ; seul le bouton Discord sous l’image ouvre l’Activity.

Cette livraison contient les fichiers du projet et le visuel, pas une maquette de message. Au déploiement, le service modifie le portail déjà enregistré au lieu de créer un deuxième message. Les anciens champs content/embeds/attachments sont vidés pendant la conversion V1 → V2 et la vue persistante garde le même custom_id de lancement.

L’image est servie publiquement à `https://altherya.magicgg.fr/assets/discord/portal-altherya.png` ; Discord doit pouvoir la télécharger sans connexion. L’Activity continue d’exiger la connexion Discord pour jouer. Une révision issue du hash de l’image évite de conserver un ancien visuel en cache. Si le domaine change, définir `ALTHERYA_PUBLIC_URL` en runtime (URL HTTPS publique, sans identifiants ni paramètres). Aucun réglage supplémentaire n’est nécessaire pour le domaine actuel.

Mettre les fichiers dans GitHub puis reconstruire et redéployer dans Coolify : le frontend doit être recompilé afin que le visuel soit copié dans le dossier dist utilisé par Docker. Conserver DISCORD_BOT_TOKEN, DISCORD_CLIENT_ID, les autres variables et le volume ACTIVITY_DB. Les sauvegardes, le tutoriel, les menus du jeu et les salons de logs ne sont pas réinitialisés.

Vérifier ensuite dans le salon 1551927225253761044 : une seule image entière et un seul bouton natif dessous. Son alignement, sa largeur et les marges sont imposés par Discord ; aucun bouton plein format sur l’image n’est simulé.

Discord ne permet pas de retirer IS_COMPONENTS_V2 d’un message déjà converti. Pour revenir à un ancien code V1, supprimer ce message et laisser ce code recréer son portail ; ne pas tenter de reconvertir le même message en V1. Le code de cette livraison conserve correctement les messages V2 lors des prochaines mises à jour.


## Résultat

Un message permanent « PORTAIL D’ALTHÉRYA », avec un bouton natif **Jouer à Altherya**, est publié dans le salon **1551927225253761044**. Le bouton ouvre l’Activity dans Discord. Il ne dirige pas vers le site public et ne poste pas un nouveau message de jeu à chaque clic.

Le message est épinglé si les permissions du bot le permettent. Son identifiant est sauvegardé dans ACTIVITY_DB et réutilisé lors des redémarrages. Le bouton reste utilisable après redémarrage grâce à sa vue persistante. Le service ne crée pas un serveur de jeu par joueur : chaque joueur affiche son propre jeu et Discord gère le lancement ou la jonction de l’Activity dans le salon. La progression reste liée au compte Discord, indépendamment de la durée de vie des sessions Discord.

## Déploiement sur votre Coolify

1. Mettre les fichiers de l’archive dans le dépôt GitHub existant. Le correctif s’applique à la version **Logs Discord** précédente. Le projet complet contient aussi tous les menus et le tutoriel illustré.
2. Dans les variables **runtime du service Activity**, conserver :
   - `DISCORD_CLIENT_ID=1529936499775242250`
   - `DISCORD_BOT_TOKEN` = token du bot **de cette même application** Discord. Ce token est distinct du Client Secret OAuth. Ne pas le mettre en Buildtime ni dans une variable VITE.
3. Inviter le bot de cette application sur le serveur s’il n’y est pas déjà. Il doit pouvoir voir le salon, lire l’historique, envoyer des messages et intégrer des liens/embeds. Autoriser l’épinglage si souhaité ; sinon épingler le portail manuellement.
4. Redéployer avec reconstruction de l’image : la dépendance API `discord.py==2.7.1` est nouvelle. Ne pas utiliser un ancien conteneur sans réinstaller ses dépendances.
5. Le service publie ou retrouve automatiquement le portail lors de la connexion du bot. Cliquer sur le bouton depuis Discord, puis tester avec un second joueur.

Conserver les autres variables OAuth, PORT, ACTIVITY_DB et le volume de données. Aucun effacement ni reset du tutoriel. Aucun nouveau port, certificat ou Interactions Endpoint URL à ajouter. Pas besoin d’activer Message Content Intent ou un intent privilégié.

## Menu Applications et cartes répétées

Le service récupère le point d’entrée global de l’application et change uniquement son `handler` vers `APP_HANDLER` (1). Son nom, ses autres propriétés et les autres commandes ne sont pas remplacés. S’il n’existe aucun point d’entrée, il en crée un nommé « jouer ». Le gestionnaire répond directement avec `LAUNCH_ACTIVITY` (12), sans follow-up public ajouté par notre bot. Depuis un autre salon, il indique le salon du portail dans une réponse privée.

Cette modification est automatique au déploiement. Il ne faut pas utiliser une synchronisation globale de commandes qui remplacerait ensuite ce point d’entrée. Notre service n’efface aucun ancien message du salon. Discord contrôle son propre affichage natif : le test dans votre client doit confirmer les cartes affichées, et chaque joueur garde sa propre vue de jeu. Nous ne pouvons pas supprimer les fenêtres de tous les joueurs ni garantir qu’un lancement effectué ailleurs dans Discord n’affichera jamais de carte native.

## Si rien n’apparaît

- Vérifier les logs du service Coolify : token absent, token invalide, application différente, salon inaccessible ou permissions insuffisantes sont signalés sans afficher de secret.
- Un token d’un autre bot peut envoyer des logs, mais ne peut pas lancer l’Activity d’Altherya. Il faut celui de l’application **1529936499775242250**.
- Si une **Interactions Endpoint URL** existe déjà dans le Developer Portal, les interactions partent vers cet endpoint et non vers le Gateway. Le service le détecte et s’arrête avant de modifier le point d’entrée. Ne pas supprimer un endpoint utilisé par une autre fonction : intégrer le bouton dans ce gestionnaire HTTP ou choisir une configuration Gateway pour cette application. Le projet Activity livré jusqu’ici n’expose pas d’endpoint d’interactions HTTP.
- Une erreur de permissions ne déclenche pas la création répétée de portails. Le service réessaie le contrôle après environ 15 minutes ; un redémarrage du service permet de retester après correction.
- Une seule connexion de ce portail utilise la même base persistante : un bail SQLite évite deux instances actives en cas de chevauchement d’un déploiement. Les réplications avec des bases différentes ne sont pas coordonnées et ne sont pas prises en charge.

## Variables facultatives et retour arrière

- `ALTHERYA_PORTAL_CHANNEL_ID` : remplace le salon intégré.
- `ALTHERYA_PORTAL_ENABLED=0` : arrête la connexion du portail. Le message existant n’est pas supprimé. Les logs/Gazette ont leur propre worker et continuent de fonctionner.
- `ALTHERYA_PORTAL_ENTRY_POINT=0` : n’administre pas le point d’entrée ; le bouton du portail fonctionne toujours. Cette variable seule ne restaure pas une modification déjà faite dans Discord.

Pour rendre le point d’entrée à Discord avant de désactiver le portail, exécuter explicitement dans l’environnement du service :

```bash
python apps/api/portal_restore_entry.py
```

Puis désactiver `ALTHERYA_PORTAL_ENABLED` et redéployer. Cette commande n’est jamais lancée automatiquement. Le message peut ensuite être supprimé manuellement si souhaité.

## Persistance et limites

Le message connu est lu par son ID. Si cet ID est absent, le service cherche un portail de ce bot parmi les messages épinglés et les 100 messages récents avant d’en créer un. Les créations utilisent aussi un nonce stable et `enforce_nonce`. Cela évite les doublons ordinaires et récupère un envoi suivi d’un arrêt avant l’enregistrement de l’ID. Un arrêt prolongé combiné à la perte de l’ID, à un portail non épinglé et à plus de 100 messages ultérieurs peut encore empêcher la récupération : aucune garantie « exactement une fois » absolue.

Aucun message n’a été publié dans votre serveur depuis cet environnement. Le portail sera installé lors de votre déploiement avec le bon token. Le Gold partagé avec Oddium n’est pas modifié ; l’Activity utilise toujours son économie SQLite séparée.

## Correction de l’archive précédente

Le fichier source `apps/game/src/data/rules.ts`, exclu par erreur de l’archive complète Logs Discord, est rétabli depuis la copie source d’origine. Les modules qui l’importent sont identiques à cette source et les tests de règles vérifient sa compatibilité. Le correctif le contient aussi. Aucun menu ni asset approuvé n’a été remplacé.
