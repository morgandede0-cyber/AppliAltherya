import unittest,tempfile,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]))
from activity import Activity

USER={'id':'666805849011912705','username':'nom_discord','global_name':'Nom Discord 🦁','avatar':None,'discriminator':'0'}
class TutorialRevisionTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.a=Activity(self.tmp.name+'/test.db');(self.uid,self.name),self.token=self.a.session('');self.a.snapshot(self.uid,self.name);self.a.bind_discord(self.uid,USER,self.token)
 def tearDown(self):self.tmp.cleanup()
 def s(self):return self.a.snapshot(self.uid,self.name)
 def action(self,action,step=None):return self.a.action(self.uid,dict(action=action,step=step))
 def complete(self):
  for step in range(5):self.action('tutorial_next',step)
  self.action('tutorial_finish',5)
 def old_revision(self):
  with self.a.conn() as c:c.execute('UPDATE activity_tutorial_revision SET revision=? WHERE user_id=?',('old-design',self.uid))
 def test_discord_name_automatically_used_and_manual_rename_refused(self):
  self.assertEqual(self.s()['name'],'Nom Discord 🦁');self.assertEqual(self.a.session(self.token)[0]['name'],'Nom Discord 🦁')
  with self.assertRaisesRegex(ValueError,'Discord'):self.a.action(self.uid,dict(action='name',name='Inventé'))
 def test_discord_name_changes_sync_all_devices(self):
  (uid,_),token=self.a.session('');self.a.snapshot(uid,'Test');self.a.bind_discord(uid,{**USER,'global_name':'Nouveau nom'},token)
  self.assertEqual(self.a.session(self.token)[0]['name'],'Nouveau nom');self.assertEqual(self.a.session(token)[0]['name'],'Nouveau nom')
 def test_username_used_when_global_name_is_missing(self):
  self.a.bind_discord(self.uid,{**USER,'global_name':None},self.token);self.assertEqual(self.s()['name'],'nom_discord')
 def test_reset_requires_new_guide_without_resetting_rewards(self):
  self.complete();before=self.s();self.old_revision();after=self.s();self.assertFalse(after['tutorial']['completed']);self.assertTrue(after['tutorial']['reward_claimed']);self.assertEqual(after['tutorial']['step'],0);self.assertEqual(after['balance'],before['balance'])
  for action in ['tutorial_cancel','tutorial_replay','daily']:
   with self.assertRaises(ValueError):self.action(action)
  self.complete();after=self.s();self.assertTrue(after['tutorial']['completed']);self.assertEqual(after['balance'],before['balance']);self.assertEqual(after['xp'],before['xp'])
  with self.a.conn() as c:self.assertEqual(c.execute('SELECT COUNT(*) FROM activity_tutorial_receipts').fetchone()[0],1)
 def test_reset_runs_once_and_progress_survives_restart(self):
  self.complete();self.old_revision();self.s();self.action('tutorial_next',0);self.a=Activity(self.a.path);self.assertEqual(self.s()['tutorial']['step'],1);self.assertFalse(self.s()['tutorial']['completed'])
 def test_admin_current_roster_resets_and_reappears_after_completion(self):
  self.complete();self.assertEqual(self.a.admin.handle(self.uid,dict(action='list'))['total'],1);self.old_revision();self.assertEqual(self.a.admin.handle(self.uid,dict(action='list'))['total'],0);self.s();self.complete();self.assertEqual(self.a.admin.handle(self.uid,dict(action='list'))['total'],1)
 def test_previous_button_is_server_backed_and_cannot_skip_forward(self):
  self.action('tutorial_next',0);self.action('tutorial_next',1);self.action('tutorial_previous',2);self.assertEqual(self.s()['tutorial']['step'],1);self.action('tutorial_next',4);self.assertEqual(self.s()['tutorial']['step'],1)
