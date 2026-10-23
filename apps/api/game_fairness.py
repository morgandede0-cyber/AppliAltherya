"""Exact public game math, derived from the same weighted slot paytable."""
from fractions import Fraction
from casino_engine import SLOT_SYMBOLS,SLOT_WEIGHTS,SLOT_TRIPLE_MULTIPLIERS

def rules():
 total=sum(SLOT_WEIGHTS);p=[Fraction(w,total) for w in SLOT_WEIGHTS]
 triple=sum((chance**3*SLOT_TRIPLE_MULTIPLIERS[s] for s,chance in zip(SLOT_SYMBOLS,p)),Fraction(0))
 refund=3*p[-1]**2*(1-p[-1]);rtp=triple+refund
 return dict(slots_return=float(rtp),notes={
  'dice':['Deux dés équilibrés : 15 résultats gagnants sur 36, 6 égalités sur 36 et 15 défaites sur 36.'],
  'coin':['Pile et Face ont chacun 50 % de chances. Un lancer précédent ne modifie pas le suivant.'],
  'rps':['L’adversaire tire uniformément parmi trois gestes : 1 chance sur 3 de gagner, de perdre ou de faire égalité.'],
  'roulette':['37 cases équiprobables, dont un seul zéro. Une chance simple gagne 18 fois sur 37 ; un numéro gagne 1 fois sur 37. Retour théorique : 36/37, soit environ 97,3 %, pour une mise valide.'],
  'slots':[f'Retour théorique de la table actuelle : {float(rtp)*100:.2f} % sur un très grand nombre de parties. Ce taux ne garantit aucun résultat sur une session.','Les trois rouleaux sont indépendants ; les symboles ne sont pas équiprobables. Deux 7 remboursent la mise ; les autres paires ne paient pas.'],
  'horses':['Le tirage pondère chaque cheval par l’inverse de sa cote. La probabilité est (1/cote) divisée par la somme des inverses des quatre cotes ; le favori peut perdre.'],
  'russian':['La balle est placée une seule fois parmi six chambres. Le barillet n’est pas mélangé entre les tours. Après chaque chambre vide, le risque du prochain tir augmente : 1 sur le nombre de chambres restantes.'],
  'blackjack':['Le croupier reste à 17, même avec un as comptant pour 11. Victoire normale : retour ×2 ; blackjack naturel : ×2,5, arrondi au Gold entier par le serveur ; égalité : mise rendue. La probabilité de gagner dépend de votre main et de vos décisions.'],
 })
