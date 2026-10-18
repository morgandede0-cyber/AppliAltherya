# Audit — illustrations des objets

## Couverture du catalogue
151 illustrations sur dix planches PNG transparentes : 120 objets d’histoire,
15 compléments d’expédition (deux plantes, neuf ressources animales, quatre
accessoires), 16 pièces narratives de quête. Les 21 ressources possédant déjà
un visuel dédié restent inchangées : les 32 ressources de vente sont couvertes.
Les outils gardent leurs atlas existants. Aucun trou dans les correspondances
canoniques histoire/ressources/accessoires du catalogue serveur.

## Intégration et conservation
Marché, inventaire du profil, forge, découvertes d’expédition et journal de quête
réutilisent les mêmes correspondances. Les noms exacts passent en priorité avant
la normalisation des accents/apostrophes/émojis. Les objets d’histoire restent
séparés des ressources, leur chapitre est conservé. Les émojis des anciens titres
d’inventaire sont retirés de l’affichage quand une vraie illustration les remplace.
Les accessoires sont illustrés mais restent indisponibles comme auparavant ;
aucune mécanique, statistique, règle de butin, récompense ou tarif n’est ajoutée.
Les pièces narratives ne deviennent pas des objets accordés à l’inventaire.

## Contrôles
- TypeScript strict et compilation Vite : succès.
- 85 tests frontend : succès, dont résolution de toutes les entrées, cellules,
  dimensions des PNG, graphies proches et association aux bons chapitres.
- 220 tests serveur : succès ; compilation Python API et bot réussie.
- Contrôle de couverture par comparaison aux catalogues Python : aucune entrée
  d’histoire, ressource ou accessoire sans illustration.
- Vérification des dix PNG : dimensions réelles, présence d’un canal alpha et contenu non vide des 151 cellules utilisées.
- 52 contrôles Playwright réussis, aucune erreur JavaScript ni image inaccessible, aux formats 1440×900, 1186×570, 390×844, 320×568 :
  inventaire, catégories séparées, chapitres, quatre cartes du marché, images
  distinctes, illustration de quête, galerie complète, conservation des soldes
  et ressources. Les réponses HTTP 304 de cache sont acceptées.
- Captures PC/mobile inspectées. Sur petit écran, les menus existants défilent.
  Le suivi des quêtes est replié pendant les contrôles des boutons du hub ;
  déployé, il peut recouvrir des boutons sur les plus petits écrans (préexistant).
- Comparaison ZIP à la version précédente : API, bot, anciens assets et
  sauvegardes inchangés. Contrôle CRC et absence de base de joueurs dans les ZIP.

## Limites
Pas de déploiement distant ni de test d’un compte dans le client Discord réel.
L’économie conserve sa base SQLite isolée ; l’intégration réelle au Gold commun
Oddium/PostgreSQL n’a pas été ajoutée ni validée. Les images sont des atlas :
une cellule est isolée par le navigateur, sans créer un PNG distinct par objet.
Les planches proviennent de l’outil d’image intégré, avec les consignes conservées
dans ASSETS_OBJETS_PROMPTS.json. La galerie catalogue.html permet de les consulter.
