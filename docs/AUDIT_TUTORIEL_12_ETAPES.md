# Complément — réinitialisation globale demandée

Cette livraison change la révision obligatoire du tutoriel. Contrairement à la livraison précédente décrite ci-dessous, les joueurs ayant déjà terminé doivent refaire les douze étapes. La liste admin filtre la nouvelle révision et repart donc à zéro immédiatement au redémarrage de l’API, même pour les comptes pas encore reconnectés. Leurs reçus de paiement sont conservés.

Tests de cette modification : 33 tests serveur tutoriel/identité/révision, dont migration depuis la révision exacte précédente, liste admin vidée puis repeuplée, absence de double paiement et reprise après redémarrage ; 249 tests client ; compilation Python API/bot et build TypeScript/Vite. Le design et les assets ne changent pas : les vérifications navigateur PC/mobile ci-dessous sont celles de la livraison précédente et ne sont pas présentées comme une nouvelle passe navigateur.

Le reset ne se réapplique pas à chaque démarrage. Aucun accès ni modification de la base de production pendant la préparation : activation après redéploiement.

---

# Vérifications du tutoriel intégré — 24 octobre 2026

## Résultat

L’affichage précédent est remplacé par douze scènes avec pose du loup adaptée. Le code utilise des parchemins vierges avec textes et boutons accessibles. Sur mobile, la scène et la feuille occupent deux zones lisibles ; sur PC, la composition loup à gauche / parchemin à droite est conservée. Le dernier bouton réclame la récompense, les autres ouvrent les vrais services avant de poursuivre.

Anciennes images retirées du projet et de l’archive. Un prébuild ciblé nettoie aussi les sept anciens fichiers lorsqu’ils proviennent d’une mise à jour copiée sur le dépôt. Le moteur de sauvegarde et les reçus sont conservés, car ils servent aux validations et à la protection des récompenses.

## Vérifications automatisées

- Compilation des modules Python API et bot : réussie.
- TypeScript et construction Vite : réussis.
- 249 tests client : réussis, dont commandes du tutoriel et journal de mises à jour (ouverture, détails, pagination).
- 31 tests tutoriel, identité du tutoriel et révision : réussis. Comprennent reprise, migration des huit anciennes découvertes, comptes distincts, erreurs, rejet des étapes/destinations invalides, paiement unique, concurrence et rollback.
- 27 tests des commandes admin : réussis, dont redémarrage ciblé conservant le reçu.
- 28 tests commerce : réussis ; 11 tests sécurité des PNJ : réussis ; 26 tests des noms serveur : réussis.
- Syntaxe des scripts navigateur : vérifiée.
- 552 assertions navigateur Chromium sur 1440×900, 1186×570, 390×844 et 320×568 : parcours complet, boutons dans le parchemin et dans la fenêtre, ouverture directe du sac, visites, retour par bouton/Echap, rechargement au milieu, fin, double validation, relecture et récompense. Aucune erreur JavaScript ni requête d’asset en échec.

## Vérifications visuelles

Captures de toutes les étapes sur PC et mobile utilisées en interne. Contrôle du loup et de ses accessoires, du changement de pose, du contenu des parchemins et du bouton en bois sombre. Espacement du pied de page et cadrage mobile ajustés après inspection. Le texte peut défiler dans sa propre zone lorsque la fenêtre manque de hauteur, sans couper les commandes.

## Sauvegarde et économie

Base temporaire uniquement. Bonus final identique : 100 Gold et 25 XP. Le paiement est atomique, fondé sur les reçus du serveur ; aucun montant fourni par le navigateur. Relecture et répétition de la requête ne paient pas de nouveau. Les joueurs déjà validés ne sont pas réinitialisés. Les anciennes visites sont conservées et remappées par destination.

Aucune modification des tarifs d’outils, des mises de Smogo, des quêtes, des données de production ou des soldes Oddium. L’accès à la base partagée de production et le lancement dans le client Discord réel ne sont pas disponibles dans cet environnement : validation à faire après redéploiement. La construction signale toujours ses avertissements connus de taille du bundle et de module audio importé à la fois statiquement et dynamiquement ; elle réussit.

## Livraison

Archive cumulative à appliquer sur le projet existant. Elle conserve les autres modifications précédemment livrées, exclut les bases, secrets, caches et dépendances. Contrôle d’intégrité ZIP et présence des quatre nouveaux assets avant livraison. Le site en production n’a pas été déployé pendant ces essais.
