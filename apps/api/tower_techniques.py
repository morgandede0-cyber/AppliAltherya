"""Tower skill definitions use the arena's existing effects and four shared slots."""
import json
from pathlib import Path
FLOORS={int(k):v for k,v in json.loads(Path(__file__).with_name('ashkar_catalog.json').read_text()).items()}
TOWER_CATALOG={
 1:dict(id='ashkar_1',slot='heavy',name='Morsure infectée',power=20,accuracy=.82,effect='bleed',description='Un impact réussi prépare 4 dégâts de saignement.',limit='Moins puissante que l’attaque lourde de base ; aucun saignement si elle manque.'),
 2:dict(id='ashkar_2',slot='light',name='Feinte du pillard',power=11,accuracy=1.,effect='evade',description='Un impact renforce temporairement votre esquive de 10 points, plafonnée à 15 %.',limit='Faibles dégâts ; les attaques rapides adverses touchent toujours.'),
 3:dict(id='ashkar_3',slot='defend',name='Pas spectral',effect='shadow',description='Garde de 25 % et 10 points d’esquive temporaire, plafonnée à 15 %.',limit='Protège moins que la garde normale ; ne permet pas d’esquiver une attaque rapide.'),
 4:dict(id='ashkar_4',slot='defend',name='Rempart déchu',effect='fortress',description='Réduit le prochain impact de 55 %.',limit='Votre prochaine attaque perd 10 % de puissance.'),
 5:dict(id='ashkar_5',slot='heavy',name='Fracas des cavernes',power=22,accuracy=.80,effect='shake',description='Un impact ébranle la cible : sa prochaine attaque perd 10 % de puissance.',limit='Puissance immédiate réduite ; aucun effet si l’attaque manque.'),
 6:dict(id='ashkar_6',slot='light',name='Furie du berserker',power=11,accuracy=1.,effect='charge',description='Un impact prépare votre prochaine attaque avec +20 % de puissance.',limit='Faibles dégâts immédiats ; le bonus ne se cumule pas.'),
 7:dict(id='ashkar_7',slot='ultimate',name='Lame corrompue',power=28,accuracy=.94,effect='pierce',description='Ignore la moitié de la garde adverse.',limit='Moins puissante que l’ultime de base sans garde adverse. Recharge : 2 actions.'),
 8:dict(id='ashkar_8',slot='defend',name='Riposte d’obsidienne',effect='counter',description='Garde de 35 %. Un impact bloqué prépare une riposte à +15 %.',limit='Protège moins que la garde normale ; aucun bonus sans impact bloqué.'),
 9:dict(id='ashkar_9',slot='ultimate',name='Sentence des abysses',power=28,accuracy=.85,effect='execute',description='+40 % de puissance contre une cible à 35 % PV ou moins.',limit='Dégâts réduits sur une cible en bonne santé. Recharge : 2 actions.'),
 10:dict(id='ashkar_10',slot='ultimate',name='Serment de Varkhaz',power=30,accuracy=.88,effect='king',description='+30 % de puissance si vos PV sont à la moitié ou moins.',limit='Inflige 3 dégâts de contrecoup au prochain tour, même en cas de raté. Recharge : 2 actions.'),
}
