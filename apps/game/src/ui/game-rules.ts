export const gameRules:Record<string,string[]>={
 blackjack:['Approchez-vous de 21 sans le dépasser. Les as valent 1 ou 11 ; les figures valent 10.','Tirez une carte ou restez. Le croupier tire jusqu’à atteindre au moins 17.'],
 roulette:['Choisissez une chance simple ou un numéro entre 0 et 36. Le zéro fait perdre les chances simples.','Un pari simple gagnant retourne 2 fois la mise ; un numéro gagnant retourne 36 fois la mise, mise comprise.'],
 slots:['Les trois rouleaux s’arrêtent successivement. Trois symboles identiques forment une combinaison gagnante.','Deux 7 restituent la mise. Les autres paires ne rapportent rien.'],
 horses:['Sélectionnez un cheval avant de lancer la course. Les cotes affichées sont celles de la manche.','Si votre cheval gagne, le serveur applique sa cote à votre mise.'],
 russian:['Jeu fictif à six chambres : vous et la hyène jouez à tour de rôle.','Le hasard décide de chaque étape. Une victoire retourne 2 fois la mise ; une défaite la perd.'],
 dice:['Vous et l’adversaire lancez un dé à six faces. Le plus grand résultat gagne.','Victoire : retour de 2 fois la mise. Égalité : mise restituée.'],
 coin:['Choisissez pile ou face avant de lancer la pièce.','Si le côté obtenu correspond à votre choix, le retour est de 2 fois la mise.'],
 rps:['Pierre bat ciseaux ; ciseaux bat feuille ; feuille bat pierre.','Victoire : retour de 2 fois la mise. Égalité : mise restituée.']
};
