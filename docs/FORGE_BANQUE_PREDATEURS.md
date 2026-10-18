# Forge et banque : intégration visuelle

Deux nouveaux décors dans le style des lieux précédemment intégrés : forge avec un ours forgeron à son enclume ; banque avec un loup argenté au comptoir. Les fonds sont vierges de données : tous les prix, quantités, états et soldes restent natifs et actualisés par les réponses du serveur.

Forge : quatre équipements, comparaison actuel/prochain palier, icônes des équipements, matériaux requis/disponibles, coût et niveau requis, amélioration conditionnelle. Les données et conditions existantes ne sont pas modifiées.

Banque de IV : Portefeuille et Banque, un formulaire Déposer/Retirer à la fois, montant, raccourcis, aperçu du nouveau solde, frais réels de retrait et confirmation. Pas de coffre central ajouté. Les entrées utilisateur restent intactes pendant l’actualisation des soldes.

Validation : TypeScript/Vite et 113 tests frontend/DOM. 48 contrôles en navigateur sur 1440×900, 1186×570, 390×844, 320×568 : quatre équipements, véritable amélioration et coût débité, dépôt de 100, retrait de 25, frais du retrait suivant, montant excessif refusé, conservation du palier et du solde après rechargement. Aucune erreur JavaScript sur ces parcours. Captures internes inspectées PC/mobile.

Les modules serveur, données de production, prix d’outils et bonus de tutoriel restent inchangés. Le test de sauvegarde utilise une base SQLite temporaire ; aucune connexion à la base PostgreSQL de production ou au client Discord de production.

Images produites avec l’outil de génération intégré, référence : décor du marchand validé. Prompts : forge médiévale avec ours forgeron à gauche et panneau de bois sombre vide à droite ; banque médiévale avec loup argenté, lunettes, registre et porte de chambre forte à gauche, panneau vide à droite. Palette chaude, bois, pierre, laiton vieilli ; aucun texte ou bouton dessiné. Les ornements sont des composants communs aux interfaces, appliqués à des dispositions propres à chaque fonction.

Installation : copier les fichiers du correctif à la racine du projet, envoyer sur GitHub puis reconstruire/redéployer avec Coolify. Les nouveaux fichiers images seuls ne remplacent pas la mise à jour du code.
