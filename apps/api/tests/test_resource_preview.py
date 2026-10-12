import sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from activity import Activity
from expedition_engine import LOOT_TABLES
class ResourcePreview(unittest.TestCase):
 def test_preview_matches_real_loot_tables_for_all_tools_and_tiers(self):
  with tempfile.TemporaryDirectory() as d:
   s=Activity(d+'/test.sqlite3').snapshot(123,'Test')
   self.assertEqual(s['loot_tables'],LOOT_TABLES)
   for key,destination in s['destinations'].items():
    for tool in destination['tools']:
     for tier in range(1,6):
      names=[n for n,minimum,weight in s['loot_tables'].get(key,{}).get(tool,[]) if minimum<=tier]
      if tool=='pickaxe':self.assertTrue(all('Bois' not in n and 'Peau' not in n and 'Viande' not in n for n in names))
      if tool=='spear':self.assertTrue(all('Bois' not in n and 'Minerai' not in n and 'Pierre' not in n for n in names))
