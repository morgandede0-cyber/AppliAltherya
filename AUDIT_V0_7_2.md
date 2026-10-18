# Altherya V0.7.2 — menus compacts, forge et résultats de l’arène

## Modifications
- Hub et marché : boutons d’origine réduits, rangés en bas de page.
- Taverne, château, ruelle, arène, jeux, casino et préparation des expéditions : décor visible, barre d’actions compacte en bas.
- Actions et retours des menus fonctionnels : boutons plus petits, cadre bleu/doré repris des assets approuvés ; les champs et choix propres à chaque formulaire restent associés à leurs informations.
- Forge : deux panneaux symétriques avec ornements d’origine, icônes d’origine, noms/paliers actualisés, matériaux et coût alignés. Sélecteurs Hache/Pioche/Lance/Sac et Améliorer en bas. Aucun ancien bouton ou zone cliquable superposé.
- Arène : message de victoire ou défaite avec ornement d’origine, nom du joueur, adversaire, Gold reçus, tours et PV. Résultat explicite envoyé par le serveur ; affichage et consultation ne versent aucune récompense. Fermeture pour lire les attaques ou retour à l’arène. Les résultats des anciennes sauvegardes restent lisibles.
- Corrections de navigation : les retours chargent le décor du lieu, les zones de la scène sont masquées pendant un menu, la barre d’actions est bloquée pendant une confirmation. Une expédition active reprend directement son suivi.
- Parchemin des annonces conservé, démarrage uniquement après signature.

## Validation
- TypeScript : compilation et build Vite réussis.
- 28 tests TypeScript et 28 tests API Python réussis (56 au total).
- Tous les modules Python de apps/api et apps/bot compilés.
- Tests serveur du résultat explicite victoire/défaite et refus d’un second règlement.
- Parcours Chromium avec dimensions PC 1440×1000 et mobile 390×844 : navigation, sélection des 4 équipements, amélioration payée avec changement du palier, dépôt bancaire, accès casino, barre de la machine à sous, marché, contrat, combat, victoire, défaite et consultation du résultat. Absence d’erreur JavaScript et de réponse HTTP en erreur lors de ces parcours.
- Les scénarios de test utilisent des personnages et une base SQLite temporaire, exclus du ZIP. Les scénarios de victoire utilisent un adversaire de test avec 1 PV pour terminer rapidement ; le règlement passe par le moteur du jeu.
- Revue des nouveaux imports et suppression des anciennes branches de navigation remplacées.
- Intégrité du ZIP vérifiée avant livraison.

## Limites conservées
Brave et Discord Activity n’ont pas été testés directement : les contrôles navigateur sont réalisés avec Chromium. Cette version conserve l’économie locale de test séparée. La connexion au personnage Discord et au Gold commun Oddium n’est pas activée ; aucune donnée de production n’a été modifiée. Les autres limites de la V0.7 restent inchangées (PvP et accessoires indisponibles, autres lieux non intégrés).

## Lancement
Extraire le ZIP dans un nouveau dossier, puis lancer DEMARRER_BRAVE.bat. Ne pas remplacer votre base de données par une base de test.
