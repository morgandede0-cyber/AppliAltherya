# Vérifications

- Compilation TypeScript et Vite réussie. Les avertissements de taille de bundle existants restent présents.
- 259 tests de régression réussis. Deux contrôles supplémentaires vérifient la forge : refus d’une demande après changement du solde, du niveau, des ressources, de la possession ou du palier ; maintien de la sélection et transmission de la seule clé d’outil choisie.
- Parcours navigateur local sur 1440 × 900, 1186 × 570, 390 × 844 et 320 × 568. Achat réel, dépôt/retrait, modes du commerce, boissons/jeux, profil/inventaire, château, tableau de bord, podium, combat jusqu’au résultat, signature de contrat et timer.
- Parcours hotbar, livres et journal des mises à jour : 120 contrôles réussis.
- Audit des chemins littéraux : 217 références, aucune manquante. Les dix nouveaux supports sont également chargés et décodés dans le parcours navigateur.
- Compilation des modules Python de l’API réussie.

Les anciennes attentes de classes graphiques des tests ont été adaptées au nouveau composant ; les assertions de données, commandes, verrouillages et résultats sont conservées. Les cibles photo sont maintenant testées dans leurs emplacements de portrait, distincts de l’image du support.

Les tests utilisent une API locale, des utilisateurs isolés et des photos simulées. La base de production, le Gold partagé avec Oddium et le lancement réel dans Discord ne sont pas directement vérifiés. Aucun déploiement de production n’a été effectué.

Les compositions sont proportionnelles et restent entièrement dans le cadre. Les listes longues, détails et journaux défilent dans leur propre zone. Les captures de contrôle restent internes et ne sont pas incluses dans les archives.
