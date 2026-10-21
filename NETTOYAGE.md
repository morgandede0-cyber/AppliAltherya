# Nettoyage Altherya — 21 octobre 2026

## Changements

193 fichiers obsolètes retirés, soit 80 987 330 octets (80,99 Mo décimaux ; 77,24 Mio) avant compression. Le manifeste NETTOYAGE_SUPPRESSIONS.json indique pour chacun le motif et l’empreinte SHA-256 d’origine.

- Ancien prototype local, styles et composants absents du graphe du client Activity.
- Anciennes illustrations remplacées, variantes inutilisées, SVG contenant des copies redondantes de l’atlas et métadonnées de génération inutilisées.
- Notes de livraison anciennes et scripts de navigateur remplacés par les 28 parcours actuels. README consolidé pour éviter des instructions d’installation contradictoires.
- Neuf anciennes définitions de vues Discord, déjà remplacées dans le même module : 155 lignes supprimées. Les sélecteurs encore utilisés par les vues actuelles sont conservés.
- Imports et variables inutilisés nettoyés. Les appels avec effets de bord (paiement, règlement de partie, entrée clandestine) restent exécutés.
- Dépendance PixiJS non utilisée retirée et fichier de verrouillage régénéré : 11 paquets retirés. Contrôles TypeScript noUnusedLocals et noUnusedParameters activés.

Les assets chargés dynamiquement sont conservés : cartes, tutoriel, chevaux, PNJ, menus, objets générés, grimoire et carte du monde. Les moteurs Python nécessaires au serveur Activity et au bot sont conservés.

Aucun changement volontaire des menus, prix des outils, bonus du tutoriel, récompenses ou règles de jeu. Aucun reset ajouté et aucune base de joueurs modifiée. Les migrations préexistantes ne sont pas supprimées.

## Vérifications

- 346 tests serveur réussis.
- 162 tests client réussis, compilation TypeScript stricte et build Vite réussis. Les 11 tests retirés concernaient uniquement le prototype local supprimé ; les tests du client Activity sont conservés.
- 17 tests du bot réussis.
- Compilation Python réussie et aucune alerte Pyflakes sur apps/api et apps/bot/tourwork.
- Tests navigateur fiabilisés : attente de la fin du lancement pour la campagne, attente du mouvement réel de la roulette plutôt qu’une pause fixe. Les contrôles du résultat, des animations et du paiement sont conservés. Aucun changement du menu.
- Correction découverte pendant les contrôles : le texte informatif du résultat des machines à sous interceptait les clics sur une fenêtre peu haute. Ce texte laisse désormais passer les clics, comme sur mobile. Le parcours de salle clandestine d’origine est conservé pour vérifier la correction.
- Script de suppression vérifié : ancien fichier identique supprimé, fichier modifié conservé, chemin extérieur refusé et seconde exécution sans effet.

- 28 parcours navigateur réussis au moins une fois sur le projet nettoyé : menus, jeux, contrôles de paiement, profils, tutoriel et affichages PC/mobile selon les tailles prévues par chaque script. Les relances ont permis de contourner les problèmes de polices du Chromium récent et les attentes fragiles des tests. Détail dans RESULTATS_NETTOYAGE.json.

Ces vérifications utilisent des données temporaires. Aucun déploiement ni test connecté à la véritable économie ou aux salons Discord n’a été effectué. Elles ne constituent pas une garantie d’absence de tout bug. Vite conserve un avertissement sur la taille du bundle, sans erreur de compilation.

## Installation

**Archive complète** : son contenu est déjà nettoyé. Remplacer les sources à la racine du dépôt en conservant les secrets et données persistantes, puis reconstruire et redéployer. Ne pas simplement fusionner les dossiers avec une ancienne copie si l’on veut faire disparaître les fichiers obsolètes.

**Mise à jour légère** : extraire le contenu de Altherya_V0_8_10 à la racine du projet existant, puis lancer NETTOYER_PROJET.bat sur Windows (ou python3 NETTOYER_PROJET.py). Le script ne supprime que les fichiers du manifeste dont le contenu est identique à l’ancienne version. Il conserve et signale les fichiers modifiés. Il ne modifie ni variables d’environnement, ni base de données, ni volume. Reconstruire ensuite le client avec npm ci puis npm run build, ou redéployer via le Dockerfile.

Conserver le port de production 10080 et les variables déjà configurées. Une ancienne version complète reste distincte du projet nettoyé ; le déploiement n’a pas été lancé automatiquement.
