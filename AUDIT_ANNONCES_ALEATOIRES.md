# Audit : annonces à rang aléatoire après signature

## Périmètre

L’adaptateur Activity `activity_jobs.py` reprend le stockage et la durée existants, mais génère huit offres non classées et tire le rang uniquement lors de l’acceptation. Le moteur historique du bot est inchangé pour préserver son interface et ses contrats. Le snapshot public des offres ne contient que `job_id` et `title` ; les données du contrat accepté comprennent son rang et sa récompense définitifs.

Aucun asset ni CSS modifié. Les changements visuels sont limités au contenu du menu et du contrat existants. Les bases et données de test ne sont pas livrées.

## Contrôles

Suite serveur complète : 220 tests réussis. 79 tests frontend et compilation TypeScript/Vite réussis ; 8 tests dédiés aux annonces, 13 tests d’économie/sauvegarde et 11 tests de l’adaptateur Activity réussis. 28 contrôles navigateur réussis sur 1440×900, 1186×570, 390×844 et 320×568, sans erreur JavaScript.

Huit tests dédiés couvrent : nombre d’offres et titres uniques ; absence de tirage avant signature et absence de rang/montant dans l’API ; stabilité au rechargement et au redémarrage ; invalidation des anciennes offres ; conservation des contrats déjà signés ; cinq rangs et fourchettes existantes ; rejet des rangs/montants envoyés par le client ; double clic et concurrence entre onglets ; interdiction de retirer avant récupération de la récompense ; répétition d’une requête ; récompense Gold/XP versée une seule fois ; rollback sur échec d’écriture.

Les tests d’économie et de sauvegarde sont adaptés pour comparer la rémunération au contrat signé plutôt qu’à l’offre non classée. Le bonus du tutoriel reste 100 Gold +25 XP et les outils/sac restent à 400 Gold. Les règles économiques, la campagne, les expéditions et le reset unique des champions ne sont pas modifiés.

Les parcours navigateur contrôlent les deux pages de quatre annonces sur PC et mobile, le contrat sans rang ni rémunération avant signature, l’annulation sans engagement, l’unique requête malgré un double clic, le rang révélé après signature, le contrat seul avec son timer, la persistance au rechargement et le versement de la récompense avec nouveau panneau de huit offres.

Compilation Python complète, suite serveur, tests frontend, compilation TypeScript/Vite et comparaison des fichiers protégés font partie des vérifications. Les captures servent à vérifier les menus localement et ne sont pas jointes à la livraison.

## Limites

Validation sur serveur local et Chromium, pas de déploiement Coolify ni de client Discord natif testés depuis cet environnement. Cette Activity conserve son économie SQLite séparée ; aucune connexion distante Oddium n’est ajoutée. Les anciens contrats sont volontairement honorés selon leurs conditions enregistrées. Le tirage indépendant ne garantit pas un rang particulier sur un petit nombre de missions.
