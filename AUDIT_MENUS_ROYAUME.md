# Audit — menus du royaume, 18 octobre 2026

## Changements
Le routage principal ouvre les nouveaux composants pour marchand, forge, taverne, boissons, jeux de taverne, chroniques, château, tableau de bord, podium et petites annonces. La banque conserve ses gestionnaires de transaction validés avec une nouvelle structure visuelle. L’arène et le profil de la livraison précédente sont inclus.

Le tableau et les contrats ne se superposent plus : le choix d’une annonce affiche son contrat, et la signature remplace ce choix par le contrat actif et son compteur. Les rangs et gains ne sont jamais inventés dans l’interface.

Le podium ajoute un lien d’avatar opaque par joueur classé. L’accès exige une session et un joueur présent dans le classement courant. Les URL de CDN sont construites exclusivement à partir des profils OAuth vérifiés. Les identifiants Discord ne sont pas ajoutés aux données publiques du classement.

## Vérifications automatisées
- Compilation Python de l’API et du bot réussie.
- 220 tests API de régression réussis.
- 9 tests dédiés aux profils Discord réussis, dont un nouveau contrôle des avatars du podium, de la nécessité d’une session et du refus d’une référence inconnue.
- 90 tests interface réussis, dont trois nouveaux : annonces et signature unique, recette réelle de forge, identité de chaque joueur du podium.
- TypeScript et compilation de production réussis.
- 100 contrôles du parcours navigateur réussis, sans erreur JavaScript, sur 1440×900, 1186×570, 390×844 et 320×568 : bornes du cadre, absence de débordement horizontal, achat réel, dépôt réel, livre, catégories, navigation, noms/photos, huit offres, signature et contrat actif. Profils et photos simulés localement ; aucune action sur le serveur Discord réel.
- Revue visuelle des captures ordinateur et mobile ; titres, actions et grilles replacés dans le cadre. Sur les petits formats, défilement interne du contenu.

## Conservation et limites
Les moteurs métier du bot, tarifs des outils et améliorations, récompense du tutoriel, marqueur de reset unique des champions et sauvegardes ne sont pas modifiés. Aucun fichier de base de données n’est livré. La vérification économique est locale sur SQLite ; aucune connexion réelle à l’économie Oddium/PostgreSQL n’a été testée ou ajoutée. Aucun déploiement distant n’est effectué.

Les animations et règles des jeux existants sont conservées ; le menu d’accès à ces jeux est refait. Les menus du monde et de la ruelle restent ceux de la version précédente, en dehors du périmètre des modèles récemment validés.
