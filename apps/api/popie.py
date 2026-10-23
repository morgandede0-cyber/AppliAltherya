"""Popie's finite daily services; called inside Activity's atomic action.

Only ordinary, explicitly catalogued resources can leave inventory. Client
amounts, rewards, time and outcomes are never authoritative.
"""
import hashlib
import json
import secrets
import time
from game_clock import today, next_midnight
from expedition_engine import RESOURCE_SELL_PRICES

BASICS=('Pierre brute','Bois de chêne','Viande de sanglier')
EXCHANGES=(('stone-wood','Pierre brute','Bois de chêne'),('wood-meat','Bois de chêne','Viande de sanglier'),('meat-stone','Viande de sanglier','Pierre brute'))
ROUTES={'safe':dict(title='Les quais surveillés',duration=300,chance=100,gold=8,xp=4),'risky':dict(title='Le chenal des brumes',duration=480,chance=70,gold=14,xp=6)}
MAX_GOLD=1_000_000_000

class Popie:
 def __init__(self,a):
  self.a=a
  with a.conn() as c:c.execute('CREATE TABLE IF NOT EXISTS activity_popie(user_id INTEGER PRIMARY KEY,payload TEXT NOT NULL DEFAULT "{}")')
 def read(self,c,uid):
  r=c.execute('SELECT payload FROM activity_popie WHERE user_id=?',(uid,)).fetchone()
  return json.loads(r[0]) if r else {}
 def offers(self,uid,day):
  seed=hashlib.sha256(f'popie:1:{uid}:{day}'.encode()).digest()
  return [dict(key=f'{day}:{i}',item=item,quantity=4+seed[i]%4,gold=(4+seed[i]%4)*RESOURCE_SELL_PRICES[item]+2,xp=3) for i,item in enumerate(BASICS)]
 def snapshot_in(self,c,uid):
  p=self.read(c,uid);day=today();stock=dict(c.execute('SELECT resource_name,quantity FROM resources WHERE user_id=?',(uid,)).fetchall())
  mission=p.get('mission');public=None
  if mission:
   # Never expose the roll before the claim. The outcome is fixed at departure.
   public={k:mission[k] for k in ('id','route','ready_at','started_at','day')}
   public.update(ROUTES[mission['route']]);public['ready']=time.time()>=mission['ready_at']
  return dict(day=day,reset_at=next_midnight(),orders=[dict(o,owned=stock.get(o['item'],0)) for o in self.offers(uid,day)],order_done=p.get('order_day')==day,exchanges=[dict(key=k,give=a,give_qty=3,receive=b,receive_qty=2,owned=stock.get(a,0)) for k,a,b in EXCHANGES],exchanges_left=max(0,3-(p.get('exchanges',0) if p.get('exchange_day')==day else 0)),mission=public,mission_done=p.get('mission_day')==day,routes=[dict(key=k,**v) for k,v in ROUTES.items()],cargo=dict(item='Bois de chêne',quantity=2,owned=stock.get('Bois de chêne',0)),last_result=p.get('last_result',''))
 @staticmethod
 def take(c,uid,item,quantity):
  if not c.execute('UPDATE resources SET quantity=quantity-? WHERE user_id=? AND resource_name=? AND quantity>=?',(quantity,uid,item,quantity)).rowcount:raise ValueError('Ressources insuffisantes dans votre inventaire.')
 @staticmethod
 def reward(c,uid,gold,xp):
  if not c.execute('UPDATE players SET wallet_gold=wallet_gold+? WHERE user_id=? AND wallet_gold+?<=?',(gold,uid,gold,MAX_GOLD)).rowcount:raise ValueError('Votre portefeuille a atteint sa limite. Déposez des Gold à la banque.')
  c.execute('UPDATE castle_profiles SET xp=xp+? WHERE user_id=?',(xp,uid))
 def action_in(self,c,uid,body):
  action=body['action'];key=body.get('key','');day=today();p=self.read(c,uid)
  if action=='port_popie_order':
   if p.get('order_day')==day:raise ValueError('Vous avez déjà honoré une commande aujourd’hui.')
   offer=next((o for o in self.offers(uid,day) if o['key']==key),None)
   if not offer:raise ValueError('Cette commande a expiré. Actualisez le comptoir.')
   self.take(c,uid,offer['item'],offer['quantity']);self.reward(c,uid,offer['gold'],offer['xp']);p['order_day']=day
   message=f"Popie : commande livrée. +{offer['gold']} Gold, +{offer['xp']} XP."
  elif action=='port_popie_exchange':
   count=p.get('exchanges',0) if p.get('exchange_day')==day else 0
   if count>=3:raise ValueError('Les trois échanges du jour ont déjà été utilisés.')
   offer=next((o for o in EXCHANGES if o[0]==key),None)
   if not offer:raise ValueError('Échange inconnu.')
   _,give,receive=offer;self.take(c,uid,give,3)
   c.execute('INSERT INTO resources VALUES(?,?,?) ON CONFLICT(user_id,resource_name) DO UPDATE SET quantity=quantity+excluded.quantity',(uid,receive,2));p.update(exchange_day=day,exchanges=count+1)
   message=f'Popie : 3 × {give} échangés contre 2 × {receive}.'
  elif action=='port_popie_start':
   if p.get('mission'):raise ValueError('Une livraison attend déjà votre retour.')
   if p.get('mission_day')==day:raise ValueError('Vous avez déjà accepté une livraison aujourd’hui.')
   route=ROUTES.get(key)
   if not route:raise ValueError('Trajet inconnu.')
   self.take(c,uid,'Bois de chêne',2);now=time.time()
   p['mission']=dict(id=secrets.token_hex(12),day=day,route=key,started_at=now,ready_at=now+route['duration'],success=secrets.randbelow(100)<route['chance']);p['mission_day']=day
   message='Popie : cargaison confiée au convoyeur. Revenez à la fin du trajet.'
  elif action=='port_popie_claim':
   m=p.get('mission')
   if not m or key!=m['id']:raise ValueError('Cette livraison a déjà été réglée ou ne vous appartient pas.')
   if time.time()<m['ready_at']:raise ValueError('La livraison est encore en route.')
   if m['success']:
    r=ROUTES[m['route']];self.reward(c,uid,r['gold'],r['xp']);message=f"Livraison réussie : +{r['gold']} Gold, +{r['xp']} XP."
   else:message='Le convoyeur a été intercepté. Les 2 bois de chêne sont perdus ; aucun Gold ni XP reçu.'
   p['last_result']=message;p.pop('mission')
  else:raise ValueError('Service de Popie inconnu.')
  c.execute('INSERT INTO activity_popie VALUES(?,?) ON CONFLICT(user_id) DO UPDATE SET payload=excluded.payload',(uid,json.dumps(p,ensure_ascii=False)))
  return message
