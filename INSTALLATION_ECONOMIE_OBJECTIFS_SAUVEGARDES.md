# Économie, objectifs et sauvegardes

## Installer

1. Extraire le correctif à la racine du projet, à côté du Dockerfile, en remplaçant les fichiers existants (ou utiliser le projet complet).
2. Effectuer la mise à jour GitHub habituelle, puis redéployer dans Coolify. Fermer et rouvrir l’Activity.
3. Conserver le volume persistant déjà monté sur /app/data. Ne pas supprimer les fichiers de données ni les volumes.

Aucun reset de comptes, du tutoriel, des quêtes ou des soldes. Le port et la configuration Discord restent identiques.

## Économie

| Élément | Avant | Maintenant |
|---|---:|---:|
| Connexion quotidienne | 200 Gold | 10 Gold |
| Trois quêtes quotidiennes | 30 Gold | 30 Gold |
| Un outil de départ | 400 Gold | 400 Gold (conservé) |
| Premier sac | 400 Gold | 400 Gold (conservé) |
| Annonce commune / 1 h | 8–25 Gold | 8–12 Gold |
| Peu commune / 1 h | 25–60 Gold | 12–18 Gold |
| Rare / 1 h | 60–120 Gold | 18–28 Gold |
| Épique / 1 h | 120–240 Gold | 28–40 Gold |
| Légendaire / 1 h | 250–500 Gold | 40–60 Gold |
| Petit larcin / 30 min | 10–35 Gold | 2–6 Gold |
| Crime réussi / 1 h | 80–160 Gold | 8–16 Gold |
| Braquage réussi | 450–900 Gold | 75–150 Gold |
| Accès clandestin jusqu’à minuit | 150 Gold | 30 Gold |
| Tournée de taverne | 300 Gold | 30 Gold |
| Objet des chroniques | 500 Gold | 30 à 175 Gold selon le groupe |

Forge aux tarifs d’origine : outil 150 / 350 / 700 / 1 400 Gold ; sac 200 / 450 / 900 / 1 800 Gold. Matériaux, niveaux requis et XP conservés. Vols de PNJ et événements monétaires de boissons ramenés environ au cinquième ; amendes ajustées aussi. Les nouveaux contrats criminels (fonction du moteur historique) sont réduits au dixième ; aucune nouvelle fonction de contrat criminel n’est ajoutée à l’Activity.

Le tutoriel reste à 100 Gold et 25 XP, une seule fois. Le premier outil et le sac coûtent ensemble 800 Gold ; la récompense du tutoriel contribue à ces achats sans les financer entièrement. Une autre profession demande d’économiser. Les 32 quêtes principales gardent le précédent réglage : 820 Gold au total, première quête 10, boss 75, XP inchangée. La vente des ressources garde ses prix pour valoriser les expéditions ; les matériaux conservés restent nécessaires à la forge. Les taux, mises et résultats des jeux et les frais de banque ne changent pas. Les multiplicateurs événementiels existants restent actifs.

Les contrats déjà acceptés conservent leur montant promis, même ancien. Les anciennes offres non acceptées sont plafonnées au nouveau barème au premier démarrage ; leur référence change pour empêcher une acceptation basée sur un ancien prix. Aucun retrait rétroactif de Gold.

Exemple de rythme (hors événements) : connexion 10 + objectifs du jour 30 = 40 Gold ; trois contrats communs accomplis apportent 24 à 36 supplémentaires. Les ressources et l’histoire s’y ajoutent. Ce sont des exemples de scénarios, pas un revenu garanti ni un équilibrage validé sur les statistiques du serveur.

## Objectifs

Dans le journal latéral droit, l’onglet « Objectifs » affiche les étapes utiles selon le personnage : remise de contrat, récompense quotidienne disponible, quête principale, premier équipement, prochaine forge, prochain lieu et niveau. Les conditions proviennent du serveur (niveau, Gold, matériaux), sans créer de nouveau déblocage ni modifier les quêtes quotidiennes. Les boutons ouvrent les fonctions existantes. Les mêmes objectifs sont accessibles depuis le journal central.

## Sauvegardes

- Une action Activity valide ensemble Gold, inventaire, XP, état de partie et reçu de requête, ou annule le tout.
- Un identifiant par opération empêche de répéter un paiement après une réponse perdue. Deux actions distinctes restent deux opérations distinctes.
- Une opération à résultat incertain est conservée dans le stockage local du navigateur (y compris après fermeture de l’Activity) et vérifiée à la reconnexion. Changer de personnage empêche de rejouer une opération sur le mauvais compte.
- Conserver un seul processus/réplica Activity sur cette base : la récupération au démarrage des mises interrompues suppose une instance unique. Les parties encore actives sont remboursées une seule fois au redémarrage, comme auparavant.
- Les bases SQLite utilisent FULL pour la durabilité et un délai d’attente en cas de verrouillage ; les connexions sont fermées après utilisation.
- Copie SQLite cohérente vérifiée au démarrage (si aucune copie de moins de 6 h), toutes les 6 h et à l’arrêt normal. Les 28 dernières copies sont conservées dans /app/data/backups par défaut. ACTIVITY_BACKUP_DIR permet de choisir un autre répertoire persistant.
- Une corruption détectée bloque l’ouverture au lieu de repartir sur une base vide. Aucune restauration automatique écrasant les données.

Copie manuelle, dans le conteneur : python apps/api/save_safety.py /app/data/activity.sqlite3 (adapter si ACTIVITY_DB est différent).

Pour restaurer : arrêter le service, conserver à part le fichier courant et ses fichiers -wal/-shm, puis remplacer la base par une copie vérifiée et redémarrer. Ne pas conserver d’anciens fichiers WAL/SHM à côté de la base restaurée. Une restauration revient à l’heure de la copie ; les actions ultérieures ne peuvent pas être recréées. Tester la copie sur une instance isolée avant une restauration réelle.

Les copies locales protègent contre une corruption ou une mauvaise mise à jour ; la perte du disque nécessite une copie externe du volume. La configuration du stockage Coolify et une copie externe ne sont pas vérifiables depuis ces fichiers.

## Limite importante

La version actuelle de l’Activity utilise SQLite séparément et refuse ECONOMY_DATABASE_URL. Le pont PostgreSQL historique reste dans les sources du bot, mais cette livraison n’active pas une économie commune Oddium. Aucun test sur la base réelle Oddium ni déploiement distant n’a été effectué. Voir AUDIT_ECONOMIE_OBJECTIFS_SAUVEGARDES.md.
