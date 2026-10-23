import sys,tempfile,json
sys.path.insert(0,'apps/api')
from activity import Activity
bad=[];values=[None,True,False,[],{},10**100,-10**100,1.5,'x']
cases=[('deposit','amount','',{}),('withdraw','amount','',{}),('sell','amount','Pierre brute',{}),('buy','key','',{}),('start','tool','elarwyn_1',{}),('start','tool_level','elarwyn_1',{'tool':'axe'}),('upgrade','key','',{}),('story_unlock','chapter','',{}),('arena_equip','slot','',{}),('arena_equip','technique','',{}),('khaz_buy','branch','',{'slot':'weapon','revision':0}),('khaz_buy','slot','',{'branch':'atk','revision':0}),('campaign_step','option','',{}),('adventure_specialize','tool','steady',{}),('adventure_training','mode','start',{}),('trade_create','item','',{'quantity':1,'price':1}),('trade_create','quantity','',{'item':'Pierre brute','price':1}),('trade_create','price','',{'item':'Pierre brute','quantity':1}),('heist_guess','guess','',{}),('job_accept','batch','x',{}),('game_start','wager','coin',{'choice':'pile'}),('game_start','choice','rps',{'wager':1}),('ashkar_start','floor','',{'revision':0})]
with tempfile.TemporaryDirectory() as d:
 a=Activity(d+'/test.db');(uid,_),token=a.session('');a.snapshot(uid,'Test');a.bind_discord(uid,dict(id='123456789012345678',username='Test',global_name='Test',avatar=None,discriminator='0'),token)
 for i in range(5):a.action(uid,dict(action='tutorial_next',step=i))
 a.action(uid,dict(action='tutorial_finish',step=5))
 with a.conn() as c:c.execute('UPDATE castle_profiles SET xp=10000 WHERE user_id=?',(uid,));c.execute('UPDATE players SET wallet_gold=10000 WHERE user_id=?',(uid,))
 n=0
 for action,field,key,extra in cases:
  for value in values:
   body=dict(action=action,key=key,**extra);body['revision']=a.snapshot(uid,'Test')['play']['revision'];body[field]=value;n+=1
   try:a.action(uid,body)
   except (ValueError,TypeError):pass
   except Exception as e:bad.append(dict(action=action,field=field,type=type(value).__name__,exception=type(e).__name__,message=str(e)))
 print(json.dumps(dict(cases=n,unexpected=bad),indent=2))
