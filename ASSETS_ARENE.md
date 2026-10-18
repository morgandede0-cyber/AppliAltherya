# Assets de l’arène

Les images de public/assets/arena sont de véritables ressources séparées des données : cadre vierge, portraits des dix champions, huit icônes. Le texte, les soldes, la vie, les actions et les résultats restent interactifs et actualisables. Les boutons sont des éléments HTML accessibles et non du texte figé dans une illustration.

Le cadre possède un fond transparent. Les portraits et icônes sont découpés depuis leurs atlas avec des fenêtres SVG. Les dimensions figurent dans src/ui/arena-art.json.

## Directions de génération
- Cadre : interface fantasy médiévale élégante, bois sombre, bronze patiné, tissu bleu pétrole, lanternes, intérieur vierge, extérieur transparent, aucune inscription.
- Champions : atlas régulier 4 × 3, dix portraits fantasy distincts correspondant aux noms et rôles existants, deux cases inutilisées ; aucun texte ni interface.
- Icônes : atlas régulier 4 × 2, épées rapides, hache lourde, frappe décisive, garde, victoire, défaite, lacération, livre ; métal patiné, palette bronze/bleu pétrole, fond transparent.

Les images générées peuvent différer légèrement des maquettes approuvées ; les informations de combat sont rendues par l’application.
