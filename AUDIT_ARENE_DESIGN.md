# Vérification de la refonte de l’arène

- 220 tests API réussis ; aucun fichier API ou bot modifié.
- 87 tests interface réussis, dont tests du surnom du serveur, de la photo, du repli sur les initiales, de la validation des mises et du verrouillage des doubles clics.
- Compilation de production réussie.
- Parcours navigateur : préparation, combat, garde, victoire, défaite, historique, acquisition et remplacement de technique ; quatre tailles d’écran (1440 × 900, 1186 × 570, 390 × 844, 320 × 568), mouvement réduit à 320 px.
- Les tests utilisent des profils Discord vérifiés de simulation et une image locale interceptée ; aucune connexion au serveur Discord réel n’est effectuée.
- Les actions, les récompenses et les données proviennent toujours du serveur ; le client n’attribue aucun gain.
- Prix des outils, bonus du tutoriel, données persistantes et marqueur de remise à zéro des champions conservés.

Sur mobile ou petite hauteur, le contenu central défile à l’intérieur du cadre ; les commandes restent accessibles. Les icônes et portraits décoratifs sont fixes, tandis que les points de vie, noms, journaux, effets et résultats se mettent à jour.
