"""Khaz'goram Activity adapter. Original forge costs, persistent auto-equipped pieces."""
import json,time
from pathlib import Path
from progression import level_from_xp
CFG=json.loads(Path(__file__).with_name('khaz_catalog.json').read_text())

def bonuses_for(eq):
 result=dict(equipment_atk_pct=0.,equipment_def_pct=0.,equipment_speed_pct=0.)
 for slot,piece in eq.items():
  if slot not in CFG['SLOTS'] or piece['branch'] not in CFG['BRANCH_LABELS']:continue
  spec=CFG['SPEC_PIECE'].get(piece['tier'],{})
  result['equipment_'+piece['branch']+'_pct']+=spec.get('advanced' if slot in CFG['ADVANCED_SLOTS'] else 'base',0)
 return {k:round(v,8) for k,v in result.items()}

class Khaz:
 def __init__(self,a):
  self.a=a
  with a.conn() as c:
   c.execute('CREATE TABLE IF NOT EXISTS legacy_wallet(user_id INTEGER PRIMARY KEY,pouciel INTEGER NOT NULL DEFAULT 0)')
   c.execute('CREATE TABLE IF NOT EXISTS legacy_equipment(user_id INTEGER NOT NULL,slot TEXT NOT NULL,branch TEXT NOT NULL,tier TEXT NOT NULL,PRIMARY KEY(user_id,slot))')
   c.execute('CREATE TABLE IF NOT EXISTS activity_khaz(user_id INTEGER PRIMARY KEY,revision INTEGER NOT NULL DEFAULT 0)')
   c.execute('CREATE TABLE IF NOT EXISTS activity_khaz_receipts(user_id INTEGER NOT NULL,revision INTEGER NOT NULL,slot TEXT NOT NULL,branch TEXT NOT NULL,old_tier TEXT,new_tier TEXT NOT NULL,gold INTEGER NOT NULL,pouciel INTEGER NOT NULL,created_at REAL NOT NULL,PRIMARY KEY(user_id,revision))')
 def ensure(self,c,uid):
  c.execute('INSERT OR IGNORE INTO legacy_wallet(user_id) VALUES(?)',(uid,));c.execute('INSERT OR IGNORE INTO activity_khaz(user_id) VALUES(?)',(uid,))
 def equipment(self,c,uid):return {r['slot']:dict(branch=r['branch'],tier=r['tier']) for r in c.execute('SELECT slot,branch,tier FROM legacy_equipment WHERE user_id=?',(uid,))}
 def bonuses_in(self,c,uid):return bonuses_for(self.equipment(c,uid))
 def bonuses(self,uid):
  with self.a.conn() as c:return self.bonuses_in(c,uid)
 def active(self,c,uid):
  if hasattr(self.a,'port') and self.a.port.active_in(c,uid):return True
  if hasattr(self.a,'tower') and self.a.tower.active_in(c,uid):return True
  row=c.execute('SELECT payload FROM activity_play WHERE user_id=?',(uid,)).fetchone()
  if row and json.loads(row[0]).get('status')=='active':return True
  row=c.execute('SELECT payload FROM campaign_progress WHERE user_id=?',(uid,)).fetchone()
  battle=json.loads(row[0]).get('battle') if row else None
  return bool(battle and not battle['finished'])
 def snapshot(self,uid):
  with self.a.conn() as c:
   self.ensure(c,uid);eq=self.equipment(c,uid);pouciel=c.execute('SELECT pouciel FROM legacy_wallet WHERE user_id=?',(uid,)).fetchone()[0];revision=c.execute('SELECT revision FROM activity_khaz WHERE user_id=?',(uid,)).fetchone()[0]
   wallet=c.execute('SELECT wallet_gold FROM players WHERE user_id=?',(uid,)).fetchone()[0];level=level_from_xp(c.execute('SELECT xp FROM castle_profiles WHERE user_id=?',(uid,)).fetchone()[0])[0];busy=self.active(c,uid)
   advanced=any(p['tier'] in ('mythique','legendaire') for p in eq.values());items=[]
   for branch in CFG['BRANCH_LABELS']:
    for slot in CFG['SLOTS']:
     owned=eq.get(slot);tier=owned['tier'] if owned and owned['branch']==branch else None;next_tier=CFG['TIER_ORDER'][CFG['TIER_ORDER'].index(tier)+1] if tier in CFG['TIER_ORDER'][:-1] else 'mythique' if not owned and slot in CFG['ADVANCED_SLOTS'] and advanced else None
     cost=CFG['POUCIEL_UPGRADE_COST'].get(next_tier) if tier else CFG['NEW_MYTHIC_COST'] if next_tier else None
     common=slot in CFG['BASE_SLOTS'];price=CFG['COMMON_GOLD_PRICES'].get(slot)
     buy_reason='Niveau 3 requis' if level<3 else 'Terminez votre partie ou votre combat' if busy else 'Emplacement déjà équipé' if owned else 'Création à partir du Mythique' if not common else 'Gold insuffisants' if wallet<price else ''
     upgrade_reason='Niveau 3 requis' if level<3 else 'Terminez votre partie ou votre combat' if busy else 'Autre voie déjà équipée' if owned and not tier else 'Qualité maximale' if tier=='legendaire' else 'Achetez cette pièce commune' if not owned and common else 'Obtenez une pièce Mythique pour ouvrir cet emplacement' if not next_tier else 'Pouciel insuffisant' if pouciel<cost else ''
     bought={**eq,slot:dict(branch=branch,tier='commun')}
     upgraded={**eq,slot:dict(branch=branch,tier=next_tier)} if next_tier else eq
     items.append(dict(buy_bonuses=bonuses_for(bought),upgrade_bonuses=bonuses_for(upgraded),slot=slot,label=CFG['SLOT_LABELS'][slot],branch=branch,tier=tier,set_name=CFG['SET_NAMES'][branch].get(tier or 'commun','Équipement ancien'),owned=owned,price=price,can_buy=not buy_reason,buy_reason=buy_reason,next_tier=next_tier,next_set=CFG['SET_NAMES'][branch].get(next_tier or ('mythique' if not owned and not common else '')),upgrade_cost=cost,can_upgrade=not upgrade_reason,upgrade_reason=upgrade_reason))
   return dict(available=level>=3,level_required=3,busy=busy,revision=revision,pouciel=pouciel,equipment=eq,bonuses=bonuses_for(eq),items=items,branches=CFG['BRANCH_LABELS'],tiers=CFG['TIER_LABELS'],slots=CFG['SLOT_LABELS'])
 def action(self,uid,body):
  branch=body.get('branch');slot=body.get('slot');action=body['action']
  if action not in ('khaz_buy','khaz_upgrade') or type(branch) is not str or branch not in CFG['BRANCH_LABELS'] or type(slot) is not str or slot not in CFG['SLOTS']:raise ValueError('Choisissez une pièce et une voie de Thorgar.')
  with self.a.conn() as c:
   c.execute('BEGIN IMMEDIATE');self.ensure(c,uid)
   level=level_from_xp(c.execute('SELECT xp FROM castle_profiles WHERE user_id=?',(uid,)).fetchone()[0])[0]
   if level<3:raise ValueError('Niveau 3 requis pour KHAZ’GORAM.')
   if self.active(c,uid):raise ValueError('Terminez votre partie ou votre combat avant de modifier votre équipement.')
   revision=c.execute('SELECT revision FROM activity_khaz WHERE user_id=?',(uid,)).fetchone()[0]
   if type(body.get('revision')) is not int or body['revision']!=revision:raise ValueError('Votre équipement a changé. Actualisez la forge.')
   eq=self.equipment(c,uid);owned=eq.get(slot);old=owned['tier'] if owned else None;gold=pouciel=0
   if action=='khaz_buy':
    if slot not in CFG['BASE_SLOTS']:raise ValueError('Ces pièces apparaissent au Mythique.')
    if owned:raise ValueError('Cet emplacement est déjà équipé.')
    gold=CFG['COMMON_GOLD_PRICES'][slot];new='commun'
    if not c.execute('UPDATE players SET wallet_gold=wallet_gold-? WHERE user_id=? AND wallet_gold>=?',(gold,uid,gold)).rowcount:raise ValueError('Gold insuffisants.')
   else:
    if body.get('expected_tier')!=old:raise ValueError('La qualité de cette pièce a changé.')
    if owned:
     if owned['branch']!=branch:raise ValueError('Cette pièce appartient à une autre voie.')
     if old not in CFG['TIER_ORDER'][:-1]:raise ValueError('Qualité maximale ou équipement ancien non reconnu.')
     new=CFG['TIER_ORDER'][CFG['TIER_ORDER'].index(old)+1];pouciel=CFG['POUCIEL_UPGRADE_COST'][new]
    else:
     if slot not in CFG['ADVANCED_SLOTS']:raise ValueError('Achetez d’abord cette pièce commune.')
     if not any(p['tier'] in ('mythique','legendaire') for p in eq.values()):raise ValueError('Obtenez d’abord une pièce Mythique.')
     new='mythique';pouciel=CFG['NEW_MYTHIC_COST']
    if not c.execute('UPDATE legacy_wallet SET pouciel=pouciel-? WHERE user_id=? AND pouciel>=?',(pouciel,uid,pouciel)).rowcount:raise ValueError('Pouciel insuffisant.')
   c.execute('INSERT INTO legacy_equipment VALUES(?,?,?,?) ON CONFLICT(user_id,slot) DO UPDATE SET branch=excluded.branch,tier=excluded.tier',(uid,slot,branch,new))
   c.execute('UPDATE activity_khaz SET revision=revision+1 WHERE user_id=?',(uid,));c.execute('INSERT INTO activity_khaz_receipts VALUES(?,?,?,?,?,?,?,?,?)',(uid,revision+1,slot,branch,old,new,gold,pouciel,time.time()));c.commit()
   return f"{CFG['SLOT_LABELS'][slot]} · {CFG['SET_NAMES'][branch][new]} · {CFG['TIER_LABELS'][new]} équipé."
