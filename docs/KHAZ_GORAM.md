# Ouverture de KHAZ’GORAM

Accès depuis Monde → Forge de Khaz’goram, au niveau 3.

Quatre écrans : accueil de Thorgar, achat, amélioration, équipement. L'achat et l'amélioration proposent les voies Attaque, Défense et Vitesse, avec quatre pièces au maximum par page, confirmation du coût et soldes actualisés après l'opération. Les pièces sont automatiquement équipées. Les menus défilent sur les petits écrans.

Les règles proviennent de `apps/bot/tourwork/legacy_world_forge.py`, sans importer ce module et ses initialisations globales. Les six pièces communes coûtent les Gold d'origine ; les améliorations coûtent respectivement 20, 45, 90 et 160 Pouciel. Après une première pièce Mythique, casque, gantelets et bottes peuvent être créés directement en Mythique pour 70 Pouciel chacun. Chaque emplacement conserve sa voie. Les pièces légendaires ne peuvent plus être améliorées.

Les tables existantes `legacy_wallet` et `legacy_equipment` sont conservées. Aucune réinitialisation, aucun Pouciel offert, aucun changement du bonus de tutoriel ou des prix des outils. Les bonus d'équipement sont pris en compte au début des prochains combats d'arène et de campagne. Les modifications d'équipement sont interdites pendant une partie ou un combat actif. Les transactions sont atomiques ; une révision et un reçu empêchent les dépenses répétées d'une même confirmation.

**Pouciels :** la Tour d’Ashkar est désormais reliée à l’Activity. Les récompenses historiques des étages 5 et 10 créditent respectivement 1 et 3 Pouciels dans `legacy_wallet`, utilisables ici. Ces récompenses sont uniques ; les revanches de la tour ne les versent pas une seconde fois. Les soldes antérieurs sont conservés.

Visuels : un décor de forge avec Thorgar et trois atlas transparents de neuf objets, un par voie. L'icône représente le type de pièce ; la qualité et le nom du set évoluent dans les données et les bordures. Le SVG découpe chaque cellule sans générer d'images supplémentaires. Prompts et mode de génération : `khaz-generation.json`.

Installation : sauvegarder la base existante, copier le contenu du dossier `Altherya_V0_8_10` de l'archive de mise à jour sur le projet existant, puis effectuer le déploiement habituel. Aucun fichier `.env` ni base de joueurs n'est inclus. Aucun déploiement distant n'a été effectué ici.

Validation : compilation TypeScript et build Vite ; 155 tests existants du client et deux nouveaux tests du menu ; huit tests Khaz serveur ; 16 tests campagne et 26 tests arène. Test navigateur avec l'API locale sur une base temporaire : ordinateur 1440×900 et mobile 390×844, quatre objets par page, confirmation d'achat, dépense exacte de 300 Gold puis 20 Pouciel, neuf emplacements, persistance après rechargement, chargement des assets et absence de débordement horizontal. Captures inspectées. L'API Discord réelle et la production n'ont pas été testées.

## Habillage du menu validé

Les cadres, boutons et onglets utilisent le kit graphique dérivé de l’image sélectionnée. Le cristal de Pouciel et la flèche d’amélioration sont isolés. Les bordures sont découpées en neuf zones par le navigateur pour préserver les angles et s’adapter aux écrans. Les noms, qualités, coûts, soldes et actions restent des éléments interactifs natifs. Les quatre objets sont paginés ; la confirmation remplace la grille et affiche la qualité actuelle et suivante.

Le kit raster a été généré avec l’outil intégré en mode édition, à partir de l’image sélectionnée exacte. Fichier : `apps/game/public/assets/khaz/ui-kit-v1.png`. Les SVG `frame-v1.svg` et `card-v1.svg` contiennent l’atlas et définissent des vues pour les bordures ; ils ne modifient pas les pixels du kit. Régions : `apps/game/src/ui/khaz-skin.json`. Prompt : `khaz-ui-generation.json`.

Les achats restent en Gold et les améliorations en Pouciels, suivant les règles existantes. Le visuel d’aperçu présentait le mot Pouciels côté achats sans tarif : cette mise à jour n’invente pas de conversion ni de prix.

Validation de cette passe : 157 tests client réussis, build TypeScript/Vite réussi ; parcours navigateur réel avec API temporaire sur ordinateur et mobile, achats et amélioration confirmés, sauvegarde après rechargement et contrôle des limites horizontales. Captures inspectées. Aucun changement du serveur, des coûts, des récompenses ou des sauvegardes. La connexion réelle Discord et la production restent hors de ces tests.
