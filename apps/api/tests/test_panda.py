import json,unittest
import test_port as harbor
from activity import Activity

class PandaTests(unittest.TestCase):
 setUp=harbor.PortTests.setUp
 tearDown=harbor.PortTests.tearDown
 make=harbor.PortTests.make
 view=harbor.PortTests.view
 act=harbor.PortTests.act
 unlock=harbor.PortTests.unlock
 def test_panda_keeps_captain_action_and_investigation(self):
  self.unlock();before=self.a.economy.get_balance(self.buyer)
  self.act('enter','capitainerie');self.act('talk','captain')
  s=self.view();self.assertTrue(s['dialogue'].startswith('Panda :'));self.assertEqual(s['phase'],1);self.assertEqual(s['clues'],[]);self.assertEqual(before,self.a.economy.get_balance(self.buyer))
 def test_saved_old_captain_dialogue_displays_panda_without_reset(self):
  self.unlock();self.act('enter','capitainerie')
  payload=dict(scene='capitainerie',phase=6,clues=['crate','seal','register'],choice='guards',dialogue='Maître du port : « Revenez avec le dossier. »')
  with self.a.conn() as c:c.execute('UPDATE activity_port SET revision=42,payload=? WHERE user_id=?',(json.dumps(payload),self.buyer))
  self.a=Activity(self.path);s=self.view();self.assertEqual(s['revision'],42);self.assertEqual(s['phase'],6);self.assertEqual(len(s['clues']),3);self.assertEqual(s['choice'],'guards');self.assertEqual(s['dialogue'],'Panda : « Revenez avec le dossier. »');self.assertIn('Panda',s['goal'])
  self.act('talk','captain');self.assertEqual(self.view()['phase'],7);self.assertTrue(self.view()['dialogue'].startswith('Panda :'))
