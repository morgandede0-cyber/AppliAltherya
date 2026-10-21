# Audit anti-triche ciblé — Altherya

21 octobre 2026. Cette passe complète `AUDIT_COMPLET.md`, à partir de l’archive complète auditée précédente. Les essais utilisent exclusivement des fichiers temporaires et des identités simulées. Aucun serveur Discord, compte réel, base de production ou solde Oddium n’a été attaqué ou modifié.

## Problèmes reproduits et corrections

### 1. Rafales de jeux pour obtenir de l’XP sans attendre les animations

**Avant correction :** 1 000 manches valides de pile ou face, chacune avec une mise de 1 Gold, ont accordé 5 000 XP en 5,271 secondes de traitement local. Le portefeuille de cet essai est passé de 10 000 à 9 998 Gold. Ce faible coût est le résultat de ce tirage, pas une garantie. Les appels ont été faits au service de jeu, sans navigateur, notifications OAuth ou latence réseau : ce temps ne mesure pas le débit du serveur de production.

Chaque manche avait bien un résultat et une mise : ce n’était pas un double paiement du même reçu. La faiblesse était l’absence de cadence serveur, qui permettait de contourner le rythme du jeu et d’accélérer le passage des niveaux.

**Correction :** délai minimal de **trois secondes entre deux nouvelles mises**, partagé entre les jeux pour le même personnage. Le délai est enregistré dans SQLite et conservé après reconnexion ou redémarrage. Changer de jeu ou falsifier une date dans la requête ne le supprime pas. Les actions d’une manche déjà engagée restent utilisables. Une tentative trop rapide est refusée avant débit, XP ou enregistrement d’une nouvelle partie.

Le client attend automatiquement le délai restant, avec ses actions verrouillées, notamment lorsque les animations sont réduites. Le serveur vérifie quand même le délai : modifier le navigateur ne suffit pas. Les montants gagnés par manche et les 5 XP d’une manche de taverne valide sont conservés.

**Après correction :** dans un test reproductible à horloge serveur figée, 1 000 tentatives dans la même fenêtre acceptent une seule manche, refusent les 999 autres et accordent 5 XP. Un second test vérifie qu’une nouvelle manche devient possible à trois secondes. Cette protection ralentit les rafales ; elle ne constitue pas une détection générale de bots ou de comptes multiples.

### 2. Récompense quotidienne et retour de la date serveur

**Reproduction avant correction :** réclamer la récompense aux dates serveur A, B, puis de nouveau A et B créditait quatre récompenses au lieu de deux : 40 Gold au lieu de 20, avec l’XP correspondante.

**Correction :** reçu persistant unique `(joueur, date)` pour la récompense quotidienne. Le bouton de disponibilité et l’objectif quotidien consultent également ce reçu. Une simple remise à zéro de l’ancien champ `last_daily` ne suffit plus à payer une seconde fois. Le reçu, le Gold et l’XP sont validés dans la même transaction.

La migration importe le dernier jour connu de chaque profil sans verser de récompense. Les anciennes dates qui n’ont jamais été historisées ne peuvent pas être reconstituées. Ce cas suppose un retour de la date du **serveur** ; changer la date du PC ou envoyer une date dans la requête ne le provoque pas.

### 3. Renouvellement du jeton de session après connexion Discord

Le jeton utilisé avant la connexion restait précédemment valable après l’authentification. Quelqu’un ayant déjà obtenu ce jeton pouvait donc le conserver. Aucun vol de compte réel n’a été démontré ; la possession préalable du jeton était une condition nécessaire.

**Correction :** association à l’identité Discord et rotation du jeton dans une seule transaction. L’ancien jeton ne donne plus accès au personnage ; les autres appareils du même joueur restent connectés. La progression et les reçus d’opérations restent rattachés au personnage canonique. Une panne simulée pendant cette opération annule l’ensemble de l’association et du renouvellement.

Contrôles HTTP et test de navigateur en iframe HTTPS : le cookie renouvelé reste compatible avec `Secure`, `HttpOnly`, `SameSite=None`, `Partitioned` et le retour sur le tutoriel déjà terminé.

### 4. Aléatoire des résultats renforcé

Les tirages actifs utilisent maintenant `SystemRandom`, alimenté par le système : cartes, dés, roulette, rouleaux, vainqueur des courses, barillet fictif, butins, code de braquage et rang des contrats. Les appels directs aux tirages du bot historique ont aussi été raccordés à cette source.

La source standard précédente n’était pas cryptographique. Aucune prédiction pratique à partir des seules réponses publiques n’a été réussie pendant cet audit : il s’agit d’un renforcement préventif. Les générateurs explicitement déterministes restent réservés aux plans quotidiens et à l’ordre cosmétique des poursuivants d’une course. Les probabilités, les paiements et les loots enregistrés auparavant ne sont pas recalculés.

## Scénarios d’attaque vérifiés

| Tentative | Contrôle et résultat final |
|---|---|
| 24 dépôts parallèles dans le même portefeuille | Aucun découvert ; seul le Gold disponible est transféré |
| 24 retraits parallèles | Un seul retrait gratuit ; frais et fortune restante cohérents |
| Même identifiant envoyé par plusieurs threads puis rejoué | Un seul débit ; changer le montant avec le même identifiant est refusé |
| 2 000 transactions mélangées | Comparaison après chaque étape avec un modèle indépendant, incluant répétitions et valeurs invalides |
| Récompense quotidienne réclamée simultanément | Un seul crédit par joueur et par jour |
| Dates et récompenses inventées côté client | Aucune influence sur le montant ou le jour serveur |
| Achat et vente répétés simultanément | Pas de copie gratuite d’équipement ni de revente du même stock |
| Mises parallèles avec la même révision | Une seule partie réglée et une seule récompense d’XP |
| Nouveau request_id et nouvelle révision à chaque tentative rapide | La cadence reste contrôlée côté serveur |
| Changement de jeu et redémarrage pour éviter le délai | Délai partagé et persistant ; pas de débit supplémentaire pendant le refus |
| Rang d’annonce relancé en acceptant les huit offres | Un seul contrat est accepté ; les autres tentatives ne tirent pas de nouveau rang |
| Contrat réclamé avant la fin puis simultanément à échéance | Pas de paiement anticipé ; un seul paiement à échéance |
| Expéditions simultanées et faux butin/heure de fin | Un seul départ actif ; pas de butin anticipé ou choisi par le client |
| Remise de quête avec récompense falsifiée et répétée | Paiement du catalogue une seule fois |
| ID d’un autre joueur ou prétention au rôle admin | L’acteur reste celui de la session ; aucun accès admin accordé |
| Techniques verrouillées ou retirées déclarées débloquées | Équipement refusé, compétences inchangées |
| Inspection des réponses du blackjack et du barillet | Paquet, carte cachée et chambre dangereuse non transmis pendant la manche |
| Session fixée avant OAuth et panne de connexion | Ancien jeton invalidé après succès ; aucune association partielle en cas d’échec |
| Réponse réseau perdue / crash pendant un achat | Scénarios de régression : idempotence et rollback conservés |

Les tests concurrents appellent le même service transactionnel que l’API, avec des threads et des identités de test. Ils ne sont pas présentés comme un essai de charge sur Discord ou sur ton hébergeur.

## Simulation économique

Un million de tirages synthétiques au total, soit 200 000 par modèle : pièce, dés, pierre-feuille-ciseaux, rouleaux et roulette rouge. Le générateur fixe du script de simulation sert à reproduire les mesures ; il n’est pas utilisé pour les résultats du jeu en production. Les rendements exacts sont calculés à partir des règles.

| Jeu / modèle | Retour moyen théorique pour 1 Gold misé, mise comprise |
|---|---:|
| Pile ou face | 1,0000 Gold |
| Dés avec égalité remboursée | 1,0000 Gold |
| Pierre-feuille-ciseaux avec égalité remboursée | 1,0000 Gold |
| Roulette européenne | 0,9730 Gold |
| Machine à sous actuelle | 0,2240 Gold |

Pour les courses, les 750 combinaisons des fourchettes de cotes ont été examinées avec les mises entières de 1 à 500 Gold. Le meilleur rendement moyen trouvé dans ce domaine est 0,7407 Gold pour 1 Gold misé. Cette exploration ne couvre pas toutes les stratégies de blackjack ni tous les événements spéciaux.

### Choix d’équilibrage signalés, sans modification

- Les jeux de taverne ordinaires ont un rendement moyen neutre en Gold, avec une variance réelle. Ils peuvent donc rester une source d’XP avec peu de perte **en moyenne**, mais désormais sans contourner la cadence serveur. Une session particulière peut perdre tout son portefeuille.
- L’événement **Gold ×2** donne volontairement une espérance positive à certains jeux : par exemple 1,5 Gold retourné en moyenne pour 1 Gold misé à pile ou face. Cela découle du bonus configuré, pas d’un reçu payé deux fois. L’événement n’a pas été neutralisé.
- La machine à sous est très défavorable au joueur : environ 22,4 % de retour théorique. Ce n’est pas un avantage exploitable par les joueurs ; sa table de gains n’a pas été modifiée.
- La cadence ne cherche pas à limiter l’XP totale obtenue en jouant longtemps de manière valide. Un plafond quotidien ou une nouvelle courbe d’XP serait une modification distincte d’équilibrage.

## Vérifications finales

- **320 tests serveur réussis**, dont les **27 nouveaux cas anti-triche**. Ces nombres se recouvrent.
- **171 tests client réussis**.
- Compilation Python et build TypeScript/Vite réussis ; avertissement de taille du bundle déjà existant.
- Six passes navigateur réussies sur la version finale : cookie en iframe HTTPS et rotation (10 contrôles), arène (40), blackjack (32), rouleaux (24), banque/livre/contrat (49), pièce sur quatre formats.
- Modèle indépendant de 2 000 opérations bancaires et rafales de 1 000 requêtes.
- Un million de tirages synthétiques et exploration des cotes des courses.
- Aucun nouveau nom Python non défini signalé par l’analyse statique. Les avertissements historiques d’imports/variables inutilisés restent ceux décrits dans le premier audit.
- Archives contrôlées : intégrité ZIP, absence de doublons, égalité des fichiers modifiés et conservation des CRC des fichiers non modifiés.

Les 27 cas anti-triche incluent le scénario de 2 000 opérations et les rafales. Les nombres de tests et d’opérations ne doivent pas être additionnés comme des parties réelles.

Les tests en navigateur concernent l’iframe HTTPS de connexion et plusieurs parcours PC/mobile : arène, pièce, blackjack, rouleaux, banque, livre du troubadour et contrat. Les captures restent des pièces d’inspection interne et ne sont pas incluses dans la livraison.

## Installation et limites

L’archive légère contient uniquement les fichiers changés depuis l’archive auditée précédente. Copier le contenu de `Altherya_V0_8_10` dans la racine du projet existant en remplaçant les fichiers correspondants, puis reconstruire et redéployer le serveur **et** le client. L’archive complète contient tous les correctifs précédents, les assets et les menus validés.

Les deux tables de protection sont créées automatiquement au démarrage. Aucune suppression de base, remise à zéro de joueurs, changement de secret ou commande de migration manuelle n’est nécessaire. Le bonus du tutoriel, les prix des outils, les montants de récompense et les visuels sont conservés.

Le Gold commun avec Oddium reste absent de cette branche SQLite. Les limites de l’audit précédent restent valables : une seule instance active par base, protections de charge du reverse proxy à vérifier, sauvegardes et permissions Discord réelles non certifiées. Le test iframe local utilise un OAuth simulé ; il ne remplace pas un lancement après déploiement dans Discord.

Cet audit ne prouve pas l’absence de toute faille, ne détecte pas tous les bots et ne garantit pas une stratégie perdante pour tous les jeux pendant tous les événements.

Pour reproduire la simulation : `python3 tools/simulate_anticheat.py` depuis le projet. Elle n’ouvre ni portefeuille de joueur ni connexion Discord et écrit `SIMULATION_ANTITRICHE.json`.
