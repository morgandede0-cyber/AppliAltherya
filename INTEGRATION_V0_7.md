# Altherya V0.7 — intégration des menus validés

Les 28 visuels approuvés sont présents dans `apps/game/public/assets/menus`. Les boutons dessinés portent des zones HTML cliquables, avec un nom accessible et un état désactivé. Les chiffres d’exemple sont couverts par les données du serveur. Le marché conserve ses quatre boutons directement dans le décor et son catalogue de quatre objets par page ; les objets d’histoire restent dans leur rayon séparé.

## Parcours intégrés

- Banque de IV : Portefeuille, Banque, Fortune, saisie du montant, boutons −/+, 100, 500, Tout, dépôt et retrait ; frais calculés selon le moteur bancaire.
- Forge : hache, pioche, lance et sac ; niveaux, recettes, ressources possédées, coût et conditions réelles.
- Petites annonces : quatre contrats par page, acceptation et confirmation, attente, récupération de Gold et d’XP.
- Château : tableau de bord, podium des trois premières fortunes, récompense journalière et suivi des six quêtes du moteur source.
- Taverne : choix des fonctions, six boissons avec réputation et délai, dés, pile ou face, pierre-feuille-ciseaux en solo ; accès aux récits du troubadour.
- Arène : champions I à X, mise facultative, techniques adaptées au niveau, défense, abandon, PV et journaux des attaques. L’illustration des combattants reste fixe.
- Ruelle : voleur, petit larcin, cibles PNJ, crimes, casier, braqueur et combinaison du coffre ; vigile avec paiement, invitation, accès VIP et expiration du passage à minuit.
- Salle clandestine : Black Jack avec cartes cachées, Tirer/Rester et calcul des as ; roulette européenne avec roue animée ; roulette russe fictive avec issue serveur ; rouleaux animés ; courses avec cotes connues avant le pari et progression des chevaux.
- Expéditions : métier, outil/palier possédé, destination, accessoires vides, confirmation du départ, compte à rebours et découvertes déjà révélées. Aucun butin futur n’est envoyé au navigateur.

Les soldes et la progression sont relus après les actions, puis toutes les quinze secondes. Les délais se comptent localement entre deux synchronisations. Les mises, gains, tirages et actions de combat appartiennent au serveur. Une révision de partie bloque les actions périmées ; les moteurs remboursent les parties actives au redémarrage.

## Ce qui reste à faire

Le personnage utilise encore un cookie du navigateur et une économie SQLite de test, distincte du bot. La connexion OAuth Discord ne relie pas encore ce personnage à un compte du bot. Les défis d’arène et de taverne contre un ami, ainsi que le vol d’un joueur, sont désactivés en attendant cette liaison. Les accessoires sont volontairement indisponibles. La Gazette, Ashkar, Khaz’goram et les interactions différées des événements de taverne restent à intégrer. Les portraits des champions sont illustratifs et ne changent pas selon le champion.

Il faut conserver `data/activity.sqlite3` et utiliser le même navigateur pour retrouver son personnage. Cette mise à jour ne contient aucune donnée personnelle ni sauvegarde de test.

## Tests de cette version

Compilation TypeScript/Vite, 28 tests TypeScript et 27 tests Python. Les tests supplémentaires couvrent les mises invalides, l’accès du vigile, les actions répétées, le zéro de roulette, les cotes des chevaux, les as, les cartes et chambres cachées, le remboursement au redémarrage, le résultat PFC, la défense et les journaux de combat, les accessoires indisponibles et le butin futur.

Des parcours de navigateur sont exécutés dans Chromium sans interface, avec captures sur écran large et un contrôle en portrait. Brave lui-même et l’environnement Discord ne sont pas disponibles ici. En portrait, le menu conserve une largeur lisible et peut se parcourir horizontalement. Le rendu Brave reste à valider sur votre machine.
