# Audit V0.3

Fonctions intégrées : marché d’équipements et ressources, collections d’histoire et lecture/déblocage des chapitres, banque, forge de la cité, récompense quotidienne du château, contrats temporisés, expéditions Elarwyn/Vorak, cueillette débutante, progression et sauvegarde serveur.

Moteurs réutilisés : economy, expedition_engine, castle_engine, story_engine, job_board_engine, progression. Leurs sources restent inchangées. L’adaptateur Activity ajoute sessions isolées, routes HTTP, récompense XP transactionnelle des contrats et rapprochement idempotent des expéditions achevées. Les tirages futurs de butin restent sur le serveur.

Tests automatisés : 13 Python (dont 9 nouveaux tests portant sur le serveur de jeu et ses routes HTTP) et 13 TypeScript. Les anciens tests TypeScript de combat/sauvegarde locale concernent les sources historiques conservées, pas le client V0.3. Les tests actifs de navigation couvrent décors, menus, retours et casino fermé. Compilation TypeScript et Vite réussie.

Cas nouveaux vérifiés : récompense quotidienne non duplicable ; dépôt/retrait conservant la fortune ; quantités invalides refusées ; achat non duplicable ; amélioration bloquée sous le niveau requis ; une seule expédition active ; fin après redémarrage avec attribution unique du butin et de l’XP ; récompense de contrat impossible avant échéance et non duplicable ; chapitre verrouillé inaccessible ; connexion à l’économie partagée refusée en mode test.

Les systèmes encore absents sont indiqués dans README.md et les menus. Aucune validation visuelle interactive Brave/Discord/mobile effectuée dans cet environnement. Aucun branchement sur le compte ou le Gold de production. La vieille sauvegarde locale n’est pas importée.
