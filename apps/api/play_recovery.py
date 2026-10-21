"""Resume paid Activity rounds; refund orphaned engine sessions atomically."""
import json
from sqlite_store import atomic
from arena_engine import BattleState
from arena_techniques import ArenaFighter,RESET_KEY
from play import total

def resumable(c, uid, p):
    kind=p.get('kind');wager=p.get('wager')
    if type(wager) is not int or wager<0:return False
    if kind in ('blackjack','russian'):
        row=c.execute("SELECT user_id,wager,game_type,status FROM casino_sessions WHERE session_id=?",(p.get('session'),)).fetchone()
        if not row or tuple(row)!=(uid,wager,kind,'active'):return False
        if kind=='russian':
            return type(p.get('danger')) is int and type(p.get('step')) is int and 1<=p['danger']<=6 and 0<=p['step']<p['danger']
        if not all(isinstance(p.get(k),list) for k in ('player','dealer','deck')):return False
        if len(p['player'])<2 or len(p['dealer'])!=2 or not p['deck']:return False
        for card in p['player']+p['dealer']+p['deck']:
            if not isinstance(card,dict) or card.get('rank') not in [str(n) for n in range(2,11)]+['J','Q','K','A'] or card.get('suit') not in ('♠','♥','♦','♣'):return False
        return total(p['player'])<21 and total(p['dealer'])<21
    if kind=='combat':
        # The one-off historical champion reset cancels old fights before changing progression.
        if not c.execute('SELECT 1 FROM activity_arena_migrations WHERE key=?',(RESET_KEY,)).fetchone():return False
        raw=p['battle'];b=BattleState(**{**raw,'fighters':[ArenaFighter(**row) for row in raw['fighters']]})
        if len(b.fighters)!=2 or b.finished or b.current!=0 or b.mode!='champion' or b.wager!=wager:return False
        # Fighter construction applies equipment HP scaling; validate saved HP instead.
        if any(not 0<row['hp']<=row['max_hp'] for row in raw['fighters']):return False
        if b.fighters[0].user_id!=uid:return False
        row=c.execute("SELECT p1,wager,mode,status FROM arena_battles WHERE battle_id=?",(b.battle_id,)).fetchone()
        return bool(row and tuple(row)==(uid,wager,'champion','active'))
    return False

def recover(play):
    with atomic(play.a.path) as c:
        pending=[];casino=set();arena=set()
        for uid,payload in c.execute('SELECT user_id,payload FROM activity_play').fetchall():
            p=json.loads(payload)
            if p.get('status')!='active':continue
            try:valid=resumable(c,uid,p)
            except (KeyError,TypeError,ValueError,AttributeError):valid=False
            if valid:
                (arena if p['kind']=='combat' else casino).add(p['battle']['battle_id'] if p['kind']=='combat' else p['session'])
            else:pending.append((uid,p))
        play.casino.recover_unfinished(preserve=casino)
        play.tavern.recover_unfinished()
        play.arena.recover_unfinished(preserve=arena)
        for uid,p in pending:
            table,idcol,ref=('arena_battles','battle_id',p.get('battle',{}).get('battle_id')) if p.get('kind')=='combat' else ('casino_sessions','session_id',p.get('session'))
            row=c.execute('SELECT status FROM '+table+' WHERE '+idcol+'=?',(ref,)).fetchone()
            refunded=bool(row and row[0] in ('refunded','cancelled'))
            message='Partie interrompue : mise remboursée au redémarrage.' if refunded else 'Partie interrompue : consultez votre solde.'
            c.execute('UPDATE activity_play SET revision=revision+1,payload=? WHERE user_id=?',(json.dumps(dict(status='refunded' if refunded else 'finished',message=message)),uid))
