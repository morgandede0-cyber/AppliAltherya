# Altherya V0.7 — menus validés et jeux interactifs

Les illustrations fournies restent les décors interactifs. Le prototype de quêtes de colis, fer et loups est remplacé par une première adaptation des fonctions originales du bot.

## Tester dans Brave

1. Arrêter l’ancien serveur avec Ctrl+C.
2. Extraire cette archive dans un nouveau dossier.
3. Double-cliquer `DEMARRER_BRAVE.bat` et garder la fenêtre ouverte.
4. Ouvrir http://localhost:8080 dans Brave et faire Ctrl+F5.

Python est nécessaire. Aucun token Discord n’est requis pour ce test. L’archive contient déjà le client compilé. Il faut ouvrir l’adresse du serveur, pas le fichier index.html directement.

## Hub et boutons fournis

Le hub utilise maintenant votre image vierge et les onze boutons illustrés fournis dans asset.zip. Chaque bouton conduit à son lieu ou menu existant ; leurs proportions sont conservées. Aucun bouton n’est incrusté définitivement dans le décor.

Les quatre boutons Histoire, Acheter, Vendre et Partir sont directement dans la scène du Marché, dès l’entrée. Aucun dialogue ou second menu n’est nécessaire. Fermer une boutique ou choisir Retour au marchand ramène à cette même scène. Les onglets Outils/Consommables/Divers et Bûcheron/Mineur/Chasseur utilisent leurs propres assets. Acheter et Vendre utilisent vos boutons de validation. Les flèches et la croix emploient les graphismes du cadre via une fenêtre SVG. États survolé/cliqué/désactivé rendus par CSS, car l’archive ne fournit pas de variantes dédiées.

## Nouveau menu du Marché

Marché → Acheter ou Vendre directement. La boutique utilise le cadre WebP fourni, avec vos images servant directement de boutons HTML cliquables. Les objets ont des illustrations vectorielles intégrées au code.

Acheter : rayons Outils, Consommables, Divers. Cliquer sur un objet pour voir sa description et son prix, Acheter pour ouvrir la confirmation, puis Confirmer pour exécuter l’opération. SOLD OUT après achat et bouton bloqué si le Gold est insuffisant. Le rayon Consommables est vide : aucun consommable n’est disponible dans le catalogue du moteur d’origine. Divers contient le sac ; les objets d’histoire sont séparés et accessibles uniquement via Histoire.

Vendre : catégories Bûcheron, Mineur, Chasseur. La cueillette est rangée avec les ressources de la forêt. Seules les ressources possédées et vendables sont affichées. Quantité avec −, +, saisie ou Tout ; prix total en direct et confirmation avant déduction. Le solde et l’inventaire sont actualisés depuis le serveur après chaque transaction.

Quatre objets par page sur écran large. Sur mobile portrait, le contenu défile horizontalement. Flèches et clavier permettent de parcourir les pages ; onglets utilisables au clavier, focus conservé dans la boutique. Échap annule une confirmation ou ferme le menu. La croix ferme la boutique, Marché revient aux quatre choix du marchand et Partir retourne au hub.

## Parcours conseillé

Château → Récompense quotidienne : 200 Gold et 20 XP, une fois par jour. Banque → déposer une partie puis retirer : Portefeuille et Banque sont séparés. Monde → Elarwyn → préparer une expédition → cueillette à mains nues : 20 minutes sans outil ni sac. Le voyage continue après fermeture du navigateur. Le butin et l’XP sont attribués à la prochaine connexion ou actualisation après son terme.

Petites annonces : cinq contrats proposés, un contrat accepté à la fois, une heure d’attente puis récupération de Gold et XP. Marché : Histoire / Acheter / Vendre / Partir. Les équipements débutants coûtent 400 Gold chacun, avec SOLD OUT après achat. La vente demande quantité puis confirmation du total. Les objets d’histoire coûtent 500 Gold ; le troubadour lit les trente chapitres d’origine, avec leurs conditions de déblocage.

Forge : les recettes, coûts et niveaux viennent du bot. Les cinq paliers sont Bois, Pierre, Fer, Or, Diamant. Acheter l’équipement débutant avant toute amélioration. Expéditions : destinations et durées d’origine, outil adapté, sac ; les deux accessoires restent vides pour le moment. Sans menus déroulants.

## Sauvegarde et limites

Le serveur utilise `data/activity.sqlite3`, une économie de test séparée de Discord/Oddium. Le navigateur identifie le personnage grâce à un cookie. Conserver ce dossier pour retrouver la progression après redémarrage ; changer de navigateur ou supprimer les cookies crée un autre personnage. La sauvegarde locale V0.2 reste dans le navigateur mais n’est pas importée : ses quêtes et son économie étaient différentes. Aucun Gold de production n’est modifié.

Le SDK OAuth est conservé, mais la connexion Discord ne lie pas encore le personnage au compte Discord. Cette version est destinée au test dans Brave, avant intégration multiutilisateur réelle.

Les menus validés, boissons et jeux solo, champions, ruelle, casino et podium sont intégrés. Les défis entre joueurs, la Gazette, KHAZ’GORAM et Ashkar restent à intégrer. Voir [INTEGRATION_V0_7.md](INTEGRATION_V0_7.md) pour le détail des fonctions et des limites.

## Coolify et développement

Dockerfile à la racine, port 8080, volume persistant à monter sur `/app/data`. Fuseau Docker Europe/Paris. Ne pas définir ECONOMY_DATABASE_URL pour ce service de test. Le bot source est conservé sans modification dans apps/bot/tourwork ; le service Activity réutilise ses moteurs indépendants de Discord.

Client : depuis apps/game, npm ci puis npm run build et npm test. API : python -m pip install -r apps/api/requirements.txt puis python -m unittest discover -s apps/api/tests -v depuis la racine. API et client doivent être servis sur la même origine. Aucun déploiement réalisé.

Voir AUDIT_MARCHE_DIRECT_V0_5_1.md et AUDIT_ASSETS_V0_5.md pour la portée des vérifications.
