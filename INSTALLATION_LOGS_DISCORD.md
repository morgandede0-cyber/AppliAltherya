# Gazette, Hall de Gloire et Logs de l’Activity

Cette version reprend le projet complet avec les menus et le tutoriel illustré. Elle ajoute le relais Discord côté API ; elle ne déploie rien automatiquement sur votre serveur.

## Installation Coolify

1. Remplacer les fichiers du projet GitHub par le contenu du dossier Altherya_V0_8_10 de l’archive. Le correctif seul s’applique à la version Tutoriel illustré livrée juste avant.
2. Dans les variables **du service Activity**, ajouter `DISCORD_BOT_TOKEN` : le token du bot présent dans le serveur Discord. Runtime uniquement, jamais Buildtime ni variable VITE. Ce token est différent de `DISCORD_CLIENT_SECRET` ; conserver ce dernier.
3. Le bot doit être invité sur votre serveur et pouvoir voir les trois salons, envoyer des messages et intégrer des liens/embeds. Pas besoin de privilège Administrateur ni de Message Content Intent pour ce relais REST.
4. Conserver les variables OAuth, PORT et ACTIVITY_DB existantes ainsi que le volume persistant contenant la base SQLite. Ne rien effacer, ne pas recréer la base. Redéployer l’application complète.
5. Lancer l’Activity depuis Discord et effectuer une action réelle : dépôt, retrait ou partie. Vérifier le message dans Logs, puis une victoire dans le Hall de Gloire.

Les salons suivants sont déjà intégrés, sans variable supplémentaire :

| Destination | Salon |
|---|---|
| Gazette | 1551927433475788880 |
| Hall de Gloire | 1551927559925538957 |
| Logs | 1551928091046314117 |

## Contenu diffusé

- Logs : achats/ventes, banque, forge, récompenses quotidiennes, contrats, chapitres débloqués, départ et fin des expéditions, taverne, ruelle, braquages, résultats des jeux et combats, modifications administrateur.
- Hall de Gloire : fin du tutoriel obligatoire, passage de niveau, victoire dans l’arène et gains nets positifs aux jeux.
- Gazette : une édition quotidienne à partir de **9 h, heure de Paris**, première édition le lendemain de l’installation. Bilan des jeux de la veille, plus gros gagnant/perdant, fortune actuelle la plus élevée et quelques faits marquants. Article masqué par le mécanisme spoiler Discord, cliquable pour le lire. Une seule édition par date, reprise le jour même si le service redémarre après 9 h. Les dates manquées pendant plusieurs jours d’arrêt ne sont pas republiées en masse.

Les noms viennent des profils Discord vérifiés. Les messages ne déclenchent aucune mention. Les consultations de menus et les tours intermédiaires de combat ne sont pas diffusés pour éviter le bruit. Les actions refusées ou sans modification ne sont pas annoncées comme réussies. Le détail d’un chapitre, le code d’un braquage et les cartes cachées ne sont jamais envoyés.

## Fonctionnement et limites

Les messages sont conservés dans la même base persistante que l’Activity. Ils partent en arrière-plan, généralement en quelques secondes ; un arriéré ou les limites Discord augmentent le délai. Sans token, la file est conservée, aucun message n’est envoyé. Aucun token n’a été ajouté dans les fichiers et aucun message de test n’a été envoyé aux salons réels.

Les confirmations d’envoi persistent après redémarrage. Les résultats ont une référence unique et les réessais utilisent `nonce` / `enforce_nonce`. Discord ne vérifie ces références que pendant quelques minutes : un doublon reste possible si le processus s’arrête après un envoi accepté mais avant son accusé local, puis redémarre longtemps après. Il ne s’agit donc pas d’une garantie « exactement une fois ».

Les notifications de gameplay sont calculées après validation à partir des changements de l’état serveur. Le point de reprise et les messages sont enregistrés ensemble ; les modifications administrateur et leur message sont dans la même transaction. Les moteurs historiques de gameplay ne partagent pas tous cette transaction : un arrêt entre leur écriture et l’observation peut retarder la récupération jusqu’à la prochaine lecture et faire perdre le détail d’une action intermédiaire. Ce relais n’est pas un registre comptable exhaustif. Les expéditions arrivées à terme sont finalisées aussi lorsque le joueur a fermé le jeu.

HTTP 429 : délai Discord respecté, pause globale persistante. HTTP 401 : pause du token ; HTTP 400/403/404 : pause du salon pendant une heure. Les messages restent en attente. Les avertissements sont visibles dans les logs Coolify, sans afficher le token. Un nouveau token peut être utilisé immédiatement ; après correction des permissions d’un salon, le délai de reprise peut atteindre une heure.

Cette Gazette couvre **les événements futurs de l’Activity**, pas les anciennes données ni les actions d’un ancien bot séparé. Si l’ancien bot publie encore sa propre Gazette dans le même salon, désactiver son ancienne publication pour éviter deux éditions distinctes. L’économie Activity reste en SQLite isolée ; ce correctif ne connecte pas la base Gold d’Oddium.

## Variables facultatives

- `ALTHERYA_DISCORD_NOTIFICATIONS=0` : désactive le worker de publication ; les actions continuent d’alimenter la file.
- `ALTHERYA_GAZETTE_CHANNEL_ID`, `ALTHERYA_HALL_CHANNEL_ID`, `ALTHERYA_LOGS_CHANNEL_ID` : remplacement des salons intégrés, runtime uniquement.

Aucun changement de port, de menus, de récompenses ou de liste d’administrateurs.
