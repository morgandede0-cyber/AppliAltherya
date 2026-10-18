# Vérifications — château intégré

- Compilation TypeScript et production Vite réussies.
- Compilation Python API et modules bot réussie.
- 93 tests interface réussis, dont protection contre les doubles clics sur la récompense quotidienne et actualisation du tableau de bord.
- 221 tests API réussis après installation des dépendances de test requises.
- 48 contrôles navigateur dédiés au château : accueil, attribution réelle de la récompense dans une base de test, désactivation après attribution, données de profil, actualisation, podium, navigation et limites de fenêtre.
- 104 contrôles navigateur de régression des services : commerce, dépôt/retrait, forge, taverne, jeux, livre original, contrats et données Discord.
- Formats contrôlés : 1440×900, 1186×570, 390×844 et 320×568. Aucun débordement horizontal ou erreur JavaScript dans ces contrôles. Captures inspectées ; centrage mobile des avatars et hauteur des cartes corrigés.

L’API et les modules du bot sont conservés octet pour octet par rapport au projet de départ. Aucun changement de prix, récompenses, règles de combat, sauvegardes ou progression. Les fichiers de la banque, du livre et du parchemin restent inchangés.

Les tests utilisent des profils, photos simulées et bases SQLite temporaires. La connexion réelle à l’économie PostgreSQL/Oddium et le déploiement Discord/Coolify ne sont pas vérifiés à distance par cette livraison.

## Assets
Génération d’images intégrée utilisée pour : un cadre vide de château conservant bois sombre, or antique, bannières, lanternes et fond bleu pétrole du modèle ; un atlas de trois piédestaux argent/or/bronze sans texte ni portraits sur fond transparent.
Les scènes de l’accueil utilisent une découpe SVG des illustrations du modèle approuvé ; les libellés, montants, pseudos et photos sont rendus par le code.
