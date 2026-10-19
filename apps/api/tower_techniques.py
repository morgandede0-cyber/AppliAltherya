"""Tower skill definitions use the arena's existing effects and four shared slots."""
import json
from pathlib import Path
FLOORS={int(k):v for k,v in json.loads(Path(__file__).with_name('ashkar_catalog.json').read_text()).items()}
TOWER_CATALOG={
 10: dict(id='ashkar_10',slot='ultimate',name='Serment de Varkhaz',power=30,accuracy=.88,effect='king',description='+30 % de puissance si vos PV sont à la moitié ou moins.',limit='Inflige 3 dégâts de contrecoup au prochain tour, même en cas de raté. Recharge : 2 actions.'),
}
