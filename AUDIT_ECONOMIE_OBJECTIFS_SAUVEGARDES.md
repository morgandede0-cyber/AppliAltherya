> Rapport de la précédente livraison. Les prix réduits des équipements sont annulés ; voir AUDIT_RESTAURATION_PRIX.md pour la correction et ses vérifications.

# Audit — économie, objectifs et sauvegardes

## Résultats

- 186 tests serveur réussis, dont la campagne complète de 32 quêtes et 13 contrôles nouveaux sur l’économie/sauvegarde.
- 72 tests interface réussis, dont les requêtes à réponse perdue, la reprise après rechargement, la validation refusée et les objectifs dynamiques.
- TypeScript strict et compilation Vite réussis ; tous les modules Python compilés ; imports des modules modifiés vérifiés.
- 31 contrôles navigateur avec zéro erreur JavaScript : PC 1440×900, paysage 810×465, mobile 390×844 et 320×568. Vérifications des panneaux, de leur repli, de leurs limites d’écran, des liens vers le marché, des prix visibles et du retour clavier. Images de contrôle PC et mobile inspectées, non livrées comme maquettes.

## Correctifs vérifiés

Achats : le budget unique du tutoriel finance un outil et un sac, sans double achat. Connexion quotidienne inférieure aux objectifs actifs. Les nouvelles annonces suivent leurs fourchettes ; un contrat signé à l’ancien tarif conserve sa promesse. Les anciennes offres non acceptées changent de référence après rééquilibrage.

Banque : deux demandes concurrentes portant le même identifiant n’agissent qu’une fois, y compris après redémarrage ; deux opérations réellement distinctes restent distinctes. Même identifiant avec un autre montant refusé. Impossible de rejouer une opération sur un personnage différent.

Atomicité : une erreur simulée après l’achat annule inventaire, Gold et reçu. Une erreur lors de l’enregistrement d’une partie annule le débit/règlement. Un vrai sous-processus arrêté brutalement après mutation ne laisse aucun demi-achat. Les mises interrompues restent remboursées une seule fois au redémarrage.

Copie : une sauvegarde SQLite vérifiée est restaurée dans une instance isolée ; session, équipement, Gold et reçus anti-doublon sont retrouvés. Soldes, ressources et récompenses historiques restent intacts après redémarrage.

Objectifs : calcul à partir des données serveur, niveau réel, Gold disponible, matériaux manquants, quête courante et lieux suivants. Aucun nouvel objectif quotidien sur une zone avancée ou une amélioration de forge. Un défaut de retour par Échap depuis un onglet du marché ayant perdu le focus a été corrigé.

## Périmètre et limites

Tous les assets, le placement des boutons du hub, les objectifs de campagne, les délais, les recettes et l’XP sont conservés. Les montants en Gold des sources régulières et des dépenses ont été rapprochés ; les revenus variables des expéditions gardent leurs prix de ressources. Le barème détaillé et les exemples de rythme figurent dans INSTALLATION_ECONOMIE_OBJECTIFS_SAUVEGARDES.md.

Les chances des jeux ne changent pas : la roulette simple retourne théoriquement 36/37 de la mise ; les machines à sous actuelles retournent environ 22,4033 % hors événements, avec leurs tables historiques. Cela ne crée pas de Gold en moyenne mais reste très punitif. L’équilibrage présenté ici concerne les gains fixes, fourchettes et prix ; il ne constitue pas une refonte des probabilités des jeux. Les événements x2 existants peuvent augmenter temporairement les gains.

Pas de test humain long sur les statistiques de production, pas de test sur Discord mobile natif (navigateur Chromium seulement), pas de déploiement distant. La configuration réelle du volume Coolify et sa copie externe restent à vérifier sur le serveur. Conserver une seule instance Activity sur la base SQLite. Les copies locales ne protègent pas contre une perte du disque ; elles ne remplacent pas une sauvegarde externe.

Gold partagé Oddium : non validé et non activé. L’Activity actuelle utilise SQLite isolément et refuse ECONOMY_DATABASE_URL ; le pont historique PostgreSQL n’a pas été modifié par cette livraison. Aucun solde distant n’a été lu ni changé.
