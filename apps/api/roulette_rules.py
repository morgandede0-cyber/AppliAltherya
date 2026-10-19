"""Single-zero European roulette: server validation before any Gold debit."""
RED={1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}
OUTSIDE={
 'red':sorted(RED),'black':sorted(set(range(1,37))-RED),
 'even':list(range(2,37,2)),'odd':list(range(1,37,2)),
 'low':list(range(1,19)),'high':list(range(19,37)),
 **{f'dozen{i}':list(range((i-1)*12+1,i*12+1)) for i in range(1,4)},
 **{f'column{i}':list(range(i,37,3)) for i in range(1,4)},
}
def covered(kind,numbers=None):
 if kind in OUTSIDE:return OUTSIDE[kind]
 if not isinstance(numbers,list) or any(type(n) is not int or not 0<=n<=36 for n in numbers) or len(set(numbers))!=len(numbers):raise ValueError('Numéros de mise invalides.')
 ns=sorted(numbers)
 if kind=='number' and len(ns)==1:return ns
 if kind=='split' and len(ns)==2:
  a,b=ns
  if (a==0 and b in (1,2,3)) or (a>0 and (b-a==3 or b-a==1 and (a-1)//3==(b-1)//3)):return ns
 if kind=='street' and (ns in ([0,1,2],[0,2,3]) or len(ns)==3 and ns[0]>0 and ns[0]%3==1 and ns==list(range(ns[0],ns[0]+3))):return ns
 if kind=='corner' and (ns==[0,1,2,3] or len(ns)==4 and ns[0]>0 and ns[0]%3!=0 and ns==[ns[0],ns[0]+1,ns[0]+3,ns[0]+4]):return ns
 if kind=='six_line' and len(ns)==6 and ns[0]>0 and ns[0]%3==1 and ns==list(range(ns[0],ns[0]+6)):return ns
 raise ValueError('Cette combinaison ne correspond pas à une mise de roulette.')
def normalise_bets(raw,wager):
 if not isinstance(raw,list) or not 1<=len(raw)<=128:raise ValueError('Placez entre 1 et 128 mises.')
 bets=[]
 for b in raw:
  if not isinstance(b,dict) or not isinstance(b.get('type'),str) or type(b.get('amount')) is not int or b['amount']<1:raise ValueError('Mise invalide.')
  ns=covered(b['type'],b.get('numbers'));bets.append(dict(type=b['type'],numbers=ns,amount=b['amount'],multiplier=36//len(ns)))
 if sum(b['amount'] for b in bets)!=wager:raise ValueError('Le total des jetons ne correspond pas à la mise.')
 return bets
def winnings(bets,number):return sum(b['amount']*b['multiplier'] for b in bets if number in b['numbers'])
