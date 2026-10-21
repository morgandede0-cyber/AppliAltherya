# Hub et ruelle sombre — intégration des décors validés

## Livraison

Cette version intègre les images validées du hub peuplé de prédateurs et de la ruelle avec le voleur panthère, le braqueur loup et le vigile ours. Les mentions « Aperçu » et le curseur peint ont été retirés avec image_gen ; les bâtiments, personnages et enseignes ont été conservés. Les nouveaux fichiers ont des noms distincts pour éviter le réemploi d’anciennes images mises en cache.

Le hub possède sept enseignes cliquables intégrées au décor : Taverne, Forge, Château, Arène, Marché, Banque et Ruelle sombre. Les quatre accès complémentaires — Petites annonces, Panneau central, Monde et Mon profil — utilisent des boutons assortis, disposés en bas et sur deux colonnes sur mobile. Il n’y a plus d’ancienne barre d’icônes du hub par-dessus les enseignes.

Dans la ruelle, cliquer sur un personnage ou son enseigne ouvre directement sa scène existante. Le retour peint en bas à gauche ramène au hub. Le survol souligne l’enseigne plutôt qu’un grand rectangle autour du personnage.

Le bouton Admin figure sur le socle central uniquement lorsque l’état authentifié renvoyé par le serveur autorise l’administration. L’API conserve son contrôle d’accès. Les permissions et identifiants autorisés ne sont pas modifiés.

Les effets discrets de la fontaine, des lanternes et de la cheminée ont été recalés sur la nouvelle image. Ils respectent le réglage d’animation, les menus ouverts et les préférences de réduction des mouvements.

## Installation

Archive de mise à jour : extraire à la racine du dépôt, dans le dossier contenant Dockerfile et apps, en acceptant les remplacements. Cette archive est cumulative pour le frontend : elle inclut toutes ses sources et les dépendances graphiques ajoutées avec les trois personnages, la salle clandestine et ces deux nouveaux décors. Envoyer les nouveaux fichiers comme les fichiers modifiés sur GitHub (`git add -A` dans votre procédure habituelle), puis redéployer dans Coolify.

Archive complète : elle reprend tout le projet courant avec cette intégration. Ne pas remplacer vos variables d’environnement, volumes de sauvegarde ou paramètres de base de données. Aucun déploiement distant n’est effectué depuis cette livraison.

## Vérifications

- Compilation TypeScript/Vite et compilation des modules Python réussies.
- 105 tests frontend/DOM réussis, incluant le graphe de navigation, les assets, les animations, les autres menus et les nouvelles commandes.
- Parcours navigateur du hub et de la ruelle sur 1440×900, 1186×570, 390×844 et 320×568 ; contrôle des destinations, des retours, des limites d’écran et de l’absence d’anciens menus superposés.
- 38 vérifications navigateur du panneau Admin réussies, dont l’ouverture du bouton sur le hub aux formats PC et mobile.
- 11 tests API Admin réussis : autorisations, liste des joueurs et opérations protégées sur base de test.
- Archives vérifiées par CRC ; comparaison des fichiers non modifiés avec l’archive précédente.

Aucun changement des règles, prix, bonus de tutoriel, sauvegardes ou mécanismes économiques. Les vérifications utilisent une base SQLite temporaire ; la connexion au PostgreSQL de production et au Gold partagé avec Oddium n’est pas testée depuis cet environnement.

## Assets

- public/assets/scenes/hub-predateurs-live.png
- public/assets/scenes/alley-predateurs-live.png

Images de référence : « La place d’Altherya, peuplée de fauves » et « Ruelle médiévale aux prédateurs anthropomorphes », validées le 18 octobre 2026. Nettoyage via image_gen intégré : retrait exclusif des légendes d’aperçu et du curseur, en conservant la composition. Les contrôles réutilisent l’atlas transparent déjà intégré au projet.
