# Altherya V0.8.1 — Menus et intégration des assets

## Corrections livrées

- Braqueur : le décor s'ouvre seul. « Planifier un braquage » ouvre la fenêtre ; ouvrir cette fenêtre ne commence pas une opération. Le lancement reste explicite, avec les restrictions serveur de réputation et de bannissement. Reprendre un braquage conserve les essais restants. La combinaison refuse les chiffres répétés ; le serveur conserve l'autorité sur le résultat.
- Vigile : même fonctionnement au clic sur « Parler au vigile », fenêtre compacte, portrait de l'asset d'origine, une seule commande pour payer ou entrer. Après paiement, le tarif disparaît au profit de l'accès valable jusqu'à minuit. Invitation et VIP conservent les règles existantes.
- Marché : nouvelle mise en page opaque en bleu et or, quatre objets maximum par page, achat et vente avec confirmation et quantité réelle. Les objets d'histoire ont leur propre rayon. Les quatre cartes et leurs commandes tiennent ensemble dans le format mobile testé. L'ancien habillage mobile « Boutique » superposé est supprimé.
- Forge : titre, ornements, outils et ressources intégrés dans des panneaux alignés. Les onglets ont des labels vivants et une sélection réelle. Coût, niveau requis, quantités détenues et prochaine amélioration viennent du serveur. Les anciens écrans superposés sont retirés du routage et du code.
- Profil : avatar Discord, nom, niveau, XP, Gold en portefeuille/en banque, statistiques, réputation, activités, équipement, ressources et objets d'histoire séparés. L'inventaire d'histoire utilise toutes les acquisitions encore détenues, même après le passage du marchand à la collection suivante.
- Monde : carte originale « Carte d’Elyndor, terres de légendes », avec Legacy, Khaz'goram et la Tour d'Ashkar, ajoutée aux assets livrés. Zoom et défilement, point cliquable de Legacy et destinations déjà prises en charge. Les voyages vers Khaz'goram/Ashkar ne sont pas ajoutés dans cette mise à jour.
- Taverne : les six cartes de boissons reprennent les illustrations d'origine dans leurs proportions, sans les bandeaux « Réputation insuffisante ». Les boissons verrouillées sont désactivées. Les limites journalières et le délai de service restent contrôlés par le serveur.
- Troubadour : livre à pages de parchemin, une page par chapitre, sommaire des seuls chapitres débloqués, lecture et navigation. Le déblocage conserve les conditions du moteur d'histoire. L'actualisation ne ramène plus le lecteur au début du texte.
- Cadrage : clipping explicite des titres et atlas pour éviter d'afficher les fragments des cellules voisines. Réinitialisation du défilement à l'ouverture d'un nouveau menu.

## Avatar Discord

L'API échange le code OAuth, récupère `/users/@me` avec le jeton vérifié puis enregistre uniquement les métadonnées publiques du profil de la session locale. Les valeurs d'avatar/nom envoyées par le navigateur ne sont pas utilisées. Les images passent par `/api/avatar` sur la même origine ; la destination CDN est construite à partir des champs vérifiés, avec délai et taille limites. Sans connexion Discord, ou si l'image échoue, le profil affiche les initiales. Aucun jeton OAuth n'est persisté dans la base.

Les variables Discord existantes restent nécessaires : `DISCORD_CLIENT_ID`, `DISCORD_CLIENT_SECRET`, `VITE_DISCORD_CLIENT_ID`. Source de référence : documentation officielle Discord, `developers/resources/user.mdx`, `developers/reference.mdx` et `developers/topics/oauth2.mdx` dans le dépôt discord/discord-api-docs.

Ce changement ajoute l'avatar à la session de test existante ; il ne fusionne pas automatiquement les personnages ou leur Gold avec une identité Discord ou avec Oddium.

## Vérifications

- TypeScript strict et compilation Vite réussis.
- 33 tests frontend réussis.
- 35 tests Python API réussis : économie existante, identité vérifiée, persistance et isolation des profils, construction des URL d'avatar, profil fourni par le client refusé, échec réseau OAuth et inventaire d'histoire séparé.
- Compilation Python API/bot réussie.
- Menus : 30 captures/parcours sur Chromium 1440 × 1000 et 390 × 844 ; achats, annulation, SOLD OUT, vente de trois unités avec débit exact du stock, quatre achats d'histoire, amélioration avec consommation exacte du Gold/matériaux, profil, carte/zoom, boissons, déblocage et navigation du livre. Aucun débordement horizontal ni erreur JavaScript. Position de lecture conservée après le polling serveur.
- Braquage : 10 contrôles PC/mobile ; lancement explicite, validation, absence de perte d'essai après erreur réseau, reprise sans redémarrage et réussite rendue d'après le serveur.
- Jeux : 20 parcours de régression PC/mobile réussis, huit jeux, mises, résultats, solde réel, animations, erreur réseau et mouvement réduit.
- Les avatars et échanges OAuth sont testés avec réponses simulées. La connexion aux vrais comptes Discord et leur photo ne sont pas testées dans l'Activity intégrée.
- ZIP : CRC, noms uniques et conformité des fichiers modifiés vérifiés. Serveur démarré depuis une extraction neuve, bundles et assets servis ; compilation depuis cette extraction réussie.

## Limites et retests

Pas de déploiement ni de validation sous Brave ou dans Discord intégré. Tests uniquement sur bases SQLite temporaires ; la base Gold Oddium de production n'est pas consultée ni modifiée. Les menus longs restent défilables verticalement sur mobile, notamment forge et livre. Les règles et récompenses des jeux, commerces et métiers ne changent pas.

Depuis `apps/game`, après installation des dépendances, compilation et installation de Chromium : `node tests/browser-menus.cjs`, `node tests/browser-heist.cjs`, `node tests/browser-games.cjs`. Les dépendances Python API doivent être installées. `CHROMIUM_EXECUTABLE`, `CHROMIUM_ARGS`, `SCREENSHOTS_DIR` et les variables de port décrites dans les tests sont facultatives. Les tests créent leurs propres bases temporaires.
