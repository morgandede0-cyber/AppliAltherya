"""Eight unranked offers; rank and reward are drawn only on commitment."""
import json,time,uuid
from secure_random import random
from job_board_engine import JobBoardStore,BoardJob,JOBS,RARITIES,REFRESH_COOLDOWN_SECONDS
BOARD_SIZE=8
class ActivityJobBoard(JobBoardStore):
 def _generate_batch(self):
  titles=tuple(dict.fromkeys(title for group in JOBS.values() for title in group))
  return uuid.uuid4().hex[:12],[BoardJob(uuid.uuid4().hex[:10],title,'unrevealed',0) for title in random.sample(titles,BOARD_SIZE)]
 def _rebalance_offers(self):
  # Retire pre-ranked boards without modifying any signed contract or its timer.
  with self._connect() as c:
   c.execute('BEGIN IMMEDIATE')
   rows=c.execute("SELECT user_id,jobs_json FROM job_board_state WHERE pending_job_json='' AND jobs_json!='[]'").fetchall()
   for uid,raw in rows:
    jobs=self._decode_jobs(raw)
    if len(jobs)==BOARD_SIZE and all(j.rarity=='unrevealed' and j.reward==0 for j in jobs):continue
    batch,offers=self._generate_batch()
    c.execute('UPDATE job_board_state SET batch_id=?,jobs_json=?,generated_at=? WHERE user_id=?',(batch,self._encode_jobs(offers),int(time.time()),uid))
 def accept_job(self,user_id,batch_id,job_id):
  uid=int(user_id);now=int(time.time())
  with self._connect() as c:
   c.execute('BEGIN IMMEDIATE');c.execute('INSERT OR IGNORE INTO job_board_state(user_id) VALUES(?)',(uid,))
   row=c.execute('SELECT * FROM job_board_state WHERE user_id=?',(uid,)).fetchone();state=self._state_from_row(row)
   if row['pending_job_json']:return False,'Terminez et réclamez votre contrat en cours.',None,state
   if state.next_board_at>now:return False,'Le panneau est encore en renouvellement.',None,state
   if not state.jobs or state.batch_id!=str(batch_id):return False,'Ce panneau n’est plus à jour. Actualisez les annonces.',None,state
   offer=next((j for j in state.jobs if j.job_id==str(job_id)),None)
   if offer is None:return False,'Cette annonce n’est plus disponible.',None,state
   rarity=self._rarity_roll();meta=RARITIES[rarity]
   job=BoardJob(offer.job_id,offer.title,rarity,random.randint(meta['gold_min'],meta['gold_max']))
   next_at=now+REFRESH_COOLDOWN_SECONDS
   c.execute("UPDATE job_board_state SET batch_id='',jobs_json='[]',generated_at=?,next_board_at=?,accepted_total=accepted_total+1,pending_job_json=?,reward_ready_at=? WHERE user_id=?",(now,next_at,json.dumps(job.to_dict(),ensure_ascii=False),next_at,uid))
  return True,f"Contrat accepté : {meta['label']} · {job.reward} Gold.",job,self.get_board(uid)
