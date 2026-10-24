import unittest
import test_trading as trade
class TavernAssetsTests(unittest.TestCase):
 setUp=trade.TradeTests.setUp
 tearDown=trade.TradeTests.tearDown
 make=trade.TradeTests.make
 def test_souvenirs_snapshot_is_read_only_owned_and_separate_from_resources(self):
  before=self.a.economy.get_balance(self.buyer)
  with self.a.conn() as c:c.execute('INSERT INTO tavern_mystery_items(user_id,item_name,quantity,obtained_at) VALUES(?,?,?,?)',(self.buyer,'Clé sans nom',2,100))
  one=self.a.snapshot(self.buyer,'Test');two=self.a.snapshot(self.other,'Autre')
  self.assertEqual(one['tavern']['mystery_items'],[dict(name='Clé sans nom',quantity=2)])
  self.assertEqual(two['tavern']['mystery_items'],[])
  self.assertNotIn('Clé sans nom',one['resources'])
  self.assertEqual(self.a.economy.get_balance(self.buyer),before)
 def test_every_awarded_event_item_has_an_exact_graphic_mapping(self):
  import json
  from pathlib import Path
  from tavern_engine import DRUNK_EVENTS
  manifest=json.loads((Path(__file__).parents[2]/'game/src/ui/tavern-item-manifest.json').read_text())
  names={e['item'] for e in DRUNK_EVENTS if e.get('item')}
  self.assertEqual(names,set(manifest))
