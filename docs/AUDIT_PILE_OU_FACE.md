# Audit Pile ou face

- TypeScript / Vite : construction réussie. Suite interface : 139 tests réussis, dont orientation des deux résultats, arrêt définitif, hauteur positive, alternance des côtés, trois contacts et audio muet.
- API : 19 tests ciblés réussis (17 existants et 2 dédiés). Les quatre combinaisons du choix et du résultat sont vérifiées avec mise et paiement, ainsi que les mises invalides et les révisions rejouées. Aucun code de production API/moteur n’est modifié ; la suite serveur complète n’a pas été relancée.
- Navigateur avec serveur réel et base temporaire : 1440×900 avec animation normale et audio activé ; 1186×570, 390×844 et 320×568 avec réduction des animations. Vérification du choix, des mises, des 64 segments de tranche, des deux faces, des rotations effectives, du verrouillage pendant le lancer, d’Échap, du résultat serveur, du portefeuille, des règles, du clavier, des dimensions et du centrage des boutons et du retour à la taverne. Aucun asset manquant ni erreur navigateur sur ces parcours réussis.
- Inspection visuelle des deux faces finales, du lancer et des mises en page PC et mobile. Un premier passage au dernier format a été interrompu par une reconstruction du bundle ; les parcours responsives ont été repris sur le bundle stable.
- Sons : trois contacts au moins déclenchés après activation du bouton Son. Sons synthétiques, pas des enregistrements.
- Archives vérifiées par CRC ; toutes les entrées non concernées et tous les fichiers de production API et moteurs sont conservés.

Limites : animation de présentation pilotée par le résultat serveur, sans moteur physique complet. Le décor et le PNJ sont fixes. Tests en navigateur local, sans déploiement dans Discord ni opération sur les données de production.
