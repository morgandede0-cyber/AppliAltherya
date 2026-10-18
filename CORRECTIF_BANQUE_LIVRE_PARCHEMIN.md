# Banque, livre et parchemin — correctif du 18 octobre 2026

## Présentations conservées
- Banque : deux panneaux illustrés Portefeuille et Banque, puis un seul espace « Gérer mes Gold » à onglets Déposer / Retirer. Aperçu du solde après opération, montant libre, 100 / 500 / Tout, confirmation et frais calculés selon les règles existantes. Le total Fortune ne crée plus de troisième panneau.
- Troubadour : retour au lecteur de livre précédent, avec ses deux pages, sa reliure, ses chapitres débloqués et son déblocage du chapitre suivant. Le code et les styles de ce livre n’ont pas été redessinés ; le routage est rétabli vers ce composant.
- Petites annonces : texture de parchemin précédente, rouleaux haut et bas, ouverture animée, signature puis sablier, compteur et progression. Une fois signé, le contrat actif remplace la liste. Le tableau de huit offres reste conservé.

## Installation
Le petit correctif s’applique sur la dernière livraison « Menus Royaume ». Copiez les fichiers aux mêmes emplacements dans votre dépôt puis redéployez dans Coolify. L’archive complète contient tous les menus et ces corrections. Ne remplacez pas vos variables privées ni votre stockage persistant.

## Vérifications
- 91 tests interface réussis, dont validation des montants, frais, verrouillage des doubles envois, onglets, conservation des valeurs et actualisation des soldes.
- 104 contrôles de navigation et des menus réussis sur quatre tailles d’écran avant le dernier ajustement de taille.
- 49 contrôles navigateur dédiés aux versions finales de la banque, du livre et du parchemin réussis sur 1440×900, 1186×570, 390×844 et 320×568. Dépôt et retrait réels sur base locale de test ; un seul formulaire visible ; titres et confirmation accessibles ; livre original ; contrat seul après signature ; compteur qui avance ; aucune erreur JavaScript.
- Compilation TypeScript / production réussie. Aucun fichier API ou moteur du bot modifié par ce correctif ; règles, récompenses, progression et données persistantes conservées.

Les tests utilisent des profils et photos de simulation. Aucun déploiement distant ni test d’une base Oddium partagée n’est effectué.
