# Altherya V0.6 — Menus dédiés

Les services disposent maintenant de leurs propres interfaces bois/or/bleu, créées en CSS et indépendantes du cadre et des images du marchand.

- Banque : soldes bourse/coffre, dépôt/retrait, saisie et raccourcis de montant, aperçu des frais exacts et transfert.
- Forge : sélection d’équipement, paliers, matériaux possédés/requis, coût et niveau, amélioration ou accès au marché.
- Annonces : quatre contrats par page, examen avant signature, attente et récupération de récompense.
- Expéditions : choix de destination, outil disponible, deux accessoires distincts, confirmation et compte à rebours.
- Personnage : expérience, équipement, ressources paginées et objets d’histoire séparés.
- Château : récompense quotidienne et accès au personnage/journal.
- Troubadour : quatre chapitres par page, conditions de déblocage et lecture dans un livre.
- Monde : destinations accessibles et indication des terres restant à intégrer.
- Journal : suivi des contrats, voyages et chapitres, accès aux activités.

Les interactions du marchand restent directement dans le hub du marché. Les menus dédiés ne chargent aucun asset de sa boutique.

Les objectifs quotidiens complets, la gazette, les jeux, l’arène et la ruelle restent à intégrer : leurs écrans le signalent. Aucune récompense ou action fictive n’est ajoutée.

Validation : compilation TypeScript/Vite, 26 tests TypeScript et 14 tests Python réussis. Les tests TypeScript incluent aussi des tests historiques. Aucun test visuel dans Brave ou Discord réalisé dans cet environnement.

Démarrage : voir README.md et les lanceurs existants. Docker/Coolify : port 8080. Conservez le volume data de votre serveur pour préserver la progression. Ne remplacez pas une base de données existante par une archive.
