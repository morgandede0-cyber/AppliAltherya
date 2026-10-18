# Huit annonces : rang tiré à la signature

L’Activity propose huit titres de missions aléatoires et distincts, présentés avec le menu existant, quatre par page. Le titre est choisi dans l’ensemble des missions, indépendamment du rang qui sera tiré plus tard. Toutes les offres ont la même présentation neutre. Aucun rang ni montant n’est attribué avant la signature, et l’API ne fournit que le titre et l’identifiant des offres.

Examiner un contrat ne déclenche aucun tirage. Le parchemin indique que rang et rémunération seront révélés après signature. « Signer et commencer » engage la mission : le serveur valide l’offre, tire son rang, tire sa rémunération dans la fourchette existante, puis enregistre le contrat et son échéance dans une même transaction. L’écran de contrat signé affiche le rang obtenu, la récompense et le timer existant.

Un rang n’est jamais sélectionné par le joueur. Recharger la page, changer d’onglet, renvoyer une requête ou redémarrer le service ne permet pas de retirer le rang d’un contrat déjà accepté. Une mission arrivée à terme bloque encore toute nouvelle acceptation tant que sa récompense n’a pas été réclamée.

## Règles conservées

| Rang | Probabilité | Gold |
| --- | --- | --- |
| Commun | 55 % | 8–12 |
| Peu commun | 25 % | 12–18 |
| Rare | 12 % | 18–28 |
| Épique | 6 % | 28–40 |
| Légendaire | 2 % | 40–60 |

Ces probabilités s’appliquent à chaque acceptation, sans quota ni garantie de rang élevé. La durée reste une heure et l’XP suit le rang réellement obtenu selon le barème existant. Aucun changement des prix des outils, du sac ou de la forge, du bonus de tutoriel ou des autres récompenses.

## Mise à jour et sauvegardes

Les anciens panneaux non signés sont remplacés automatiquement par huit offres neutres. Leur ancien identifiant de lot devient invalide. Les contrats déjà signés conservent leur rang, leur montant (même un ancien montant élevé), leur échéance et leur droit à récompense. Les nouveaux panneaux neutres sont conservés au redémarrage ; la simple ouverture du menu ne renouvelle pas la sélection.

Remplacer les fichiers avec le correctif ou le projet complet, envoyer sur GitHub, puis reconstruire et redéployer dans Coolify. Conserver le volume et la même base `ACTIVITY_DB`. Aucune nouvelle variable ou commande SQL requise. Ne pas effacer les données. Cette mise à jour ne réexécute pas le reset unique des champions déjà enregistré.

## Design

Les images, cadres, boutons, parchemin, couleurs, CSS et emplacements existants sont conservés. Les textes et les informations des annonces changent : rang masqué sur les offres, engagement au tirage dans le contrat non signé, rang et récompense réels sur le contrat signé. Le sceau avant signature est neutre pour ne pas suggérer de rareté. La navigation PC/mobile existante est conservée.
