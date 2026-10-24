import sys,tempfile,unittest,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]))
from activity import Activity
from campaign import QUESTS
class QuestReadingTests(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();self.a=Activity(self.t.name+'/db');(self.uid,self.name),_=self.a.session('');self.a.snapshot(self.uid,self.name)
 def tearDown(self):self.t.cleanup()
 def test_contents_never_publish_future_story_or_solution(self):
  c=self.a.campaign.snapshot(self.uid);self.assertEqual(len(c['entries']),32)
  self.assertEqual(c['entries'][0]['status'],'current')
  for e in c['entries'][1:]:self.assertEqual(set(e),{'index','id','season','chapter','min_level','status','title'});self.assertEqual(e['title'],'Quête scellée');self.assertEqual(e['status'],'locked')
  for step in c['quest']['steps']:self.assertTrue(step['hint']);self.assertNotIn('answer',step)
 def test_journal_is_read_only_and_receipts_unlock_only_completed_records(self):
  before=self.a.snapshot(self.uid,self.name)['balance']
  with self.a.conn() as db:db.execute('INSERT INTO campaign_receipts VALUES(?,?,?,?,?)',(self.uid,QUESTS[0]['id'],10,20,1));db.execute('UPDATE campaign_progress SET quest_index=1 WHERE user_id=?',(self.uid,))
  c=self.a.campaign.snapshot(self.uid);self.assertEqual(c['entries'][0]['status'],'completed');self.assertTrue(c['entries'][0]['objectives']);self.assertEqual(c['entries'][1]['status'],'current')
  for _ in range(3):self.a.campaign.snapshot(self.uid)
  self.assertEqual(self.a.snapshot(self.uid,self.name)['balance'],before)
