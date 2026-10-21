from __future__ import annotations
import sqlite3
import hashlib, itertools, json, random
from shared_economy import connect_shared
from datetime import datetime, date
from pathlib import Path
from progression import level_from_xp, XP_REWARDS
from admin_engine import event_multiplier

from economy_balance import DAILY_GOLD, DAILY_QUEST_GOLD
DAILY_REWARD = DAILY_GOLD
DAILY_XP = 20

# Objectifs classiques disponibles dès Legacy, sans lieu avancé ni amélioration.
QUEST_GLOBAL_GOLD = DAILY_QUEST_GOLD
QUEST_GLOBAL_XP = 75
QUESTS = {
    'combat': ('Participer à un combat d’arène', 1, 'combat'),
    'daily_bonus': ('Récupérer la récompense quotidienne', 1, 'daily_bonus'),
    'arena_win': ('Gagner un combat d’arène', 1, 'arena_win'),
    'tavern_game': ('Participer à un jeu de Taverne', 1, 'tavern_game'),
    'expedition': ('Terminer une expédition au choix', 1, 'expedition'),
}



class CastleStore:
    def __init__(self, db_path: str|Path):
        self.db_path=Path(db_path); self.db_path.parent.mkdir(parents=True,exist_ok=True); self._init()
    def _c(self):
        c=connect_shared(self.db_path,timeout=10); c.row_factory=sqlite3.Row; return c
    def _today(self): return datetime.now().date().isoformat()
    def _init(self):
        with self._c() as c:
            c.execute('''CREATE TABLE IF NOT EXISTS castle_profiles(user_id INTEGER PRIMARY KEY, xp INTEGER NOT NULL DEFAULT 0, combats INTEGER NOT NULL DEFAULT 0, wins INTEGER NOT NULL DEFAULT 0, losses INTEGER NOT NULL DEFAULT 0, expeditions INTEGER NOT NULL DEFAULT 0, casino_games INTEGER NOT NULL DEFAULT 0, quests_completed INTEGER NOT NULL DEFAULT 0, member_since TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, last_daily TEXT)''')
            c.execute('''CREATE TABLE IF NOT EXISTS castle_daily_progress(user_id INTEGER NOT NULL, day TEXT NOT NULL, quest_key TEXT NOT NULL, progress INTEGER NOT NULL DEFAULT 0, claimed INTEGER NOT NULL DEFAULT 0, PRIMARY KEY(user_id,day,quest_key))''')
            c.execute('CREATE TABLE IF NOT EXISTS castle_daily_plans(user_id INTEGER NOT NULL, day TEXT NOT NULL, plan_json TEXT NOT NULL, PRIMARY KEY(user_id,day))')
            c.execute('CREATE TABLE IF NOT EXISTS castle_daily_receipts(user_id INTEGER NOT NULL,day TEXT NOT NULL,PRIMARY KEY(user_id,day))')
            # Preserve the known last claim when upgrading an existing database.
            c.execute("INSERT OR IGNORE INTO castle_daily_receipts(user_id,day) SELECT user_id,last_daily FROM castle_profiles WHERE last_daily IS NOT NULL AND last_daily!=''")
            c.execute('''CREATE TABLE IF NOT EXISTS castle_levelups(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                old_level INTEGER NOT NULL,
                new_level INTEGER NOT NULL,
                old_hp INTEGER NOT NULL,
                new_hp INTEGER NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                consumed INTEGER NOT NULL DEFAULT 0
            )''')
            c.commit()
    def ensure(self,user_id):
        with self._c() as c: c.execute('INSERT OR IGNORE INTO castle_profiles(user_id) VALUES(?)',(int(user_id),)); c.commit()
    def _sync_level(self,c,uid):
        row=c.execute('SELECT xp FROM castle_profiles WHERE user_id=?',(int(uid),)).fetchone()
        if not row: return
        level=level_from_xp(int(row['xp']))[0]
        c.execute('INSERT OR IGNORE INTO expedition_profiles(user_id) VALUES(?)',(int(uid),))
        c.execute('UPDATE expedition_profiles SET player_level=? WHERE user_id=?',(level,int(uid)))
    def current_level(self,user_id):
        p=self.profile(user_id)
        return level_from_xp(int(p['xp']))[0]
    def profile(self,user_id):
        self.ensure(user_id)
        with self._c() as c: return dict(c.execute('SELECT * FROM castle_profiles WHERE user_id=?',(int(user_id),)).fetchone())
    @staticmethod
    def _base_hp_for_level(level):
        return 100 + 10 * (max(1, int(level)) - 1)

    def _queue_levelups(self,c,uid,before_xp,after_xp):
        old_level=level_from_xp(int(before_xp))[0]
        new_level=level_from_xp(int(after_xp))[0]
        if new_level <= old_level:
            return
        for lvl in range(old_level + 1, new_level + 1):
            prev=lvl-1
            c.execute('''INSERT INTO castle_levelups(user_id,old_level,new_level,old_hp,new_hp) VALUES(?,?,?,?,?)''',
                      (int(uid),prev,lvl,self._base_hp_for_level(prev),self._base_hp_for_level(lvl)))

    def pending_levelups(self,user_id,consume=True):
        uid=int(user_id)
        with self._c() as c:
            rows=c.execute('SELECT * FROM castle_levelups WHERE user_id=? AND consumed=0 ORDER BY id',(uid,)).fetchall()
            out=[dict(r) for r in rows]
            if consume and rows:
                c.execute('UPDATE castle_levelups SET consumed=1 WHERE user_id=? AND consumed=0',(uid,)); c.commit()
        return out

    def add_xp(self,user_id,amount):
        self.ensure(user_id); uid=int(user_id)
        with self._c() as c:
            before=int(c.execute('SELECT xp FROM castle_profiles WHERE user_id=?',(uid,)).fetchone()['xp'])
            amount=max(0,int(amount))*event_multiplier(self.db_path,'xp_x2')
            c.execute('UPDATE castle_profiles SET xp=xp+? WHERE user_id=?',(amount,uid))
            after=before+amount
            self._queue_levelups(c,uid,before,after)
            self._sync_level(c,uid); c.commit()
        return amount
    def quest_config(self,user_id):
        uid=int(user_id);day=self._today()
        # A saved server plan survives reconnects, restarts and reputation changes.
        # Adjacent days use distinct families, selected in a player-specific order.
        seed=int(hashlib.sha256(f'altherya-daily-v1:{uid}'.encode()).hexdigest(),16)
        choices=list(itertools.combinations(('arena','tavern','expedition','daily'),3))
        random.Random(seed).shuffle(choices)
        ordinal=date.fromisoformat(day).toordinal()
        rng=random.Random(seed+ordinal)
        generated={}
        for family in choices[ordinal%len(choices)]:
            key=rng.choice(('combat','arena_win')) if family=='arena' else {'tavern':'tavern_game','expedition':'expedition','daily':'daily_bonus'}[family]
            label,target,event=QUESTS[key]
            if key=='tavern_game':
                target=rng.choice((1,2));label=f'Participer à {target} jeu'+('x' if target>1 else '')+' de Taverne'
            generated[key]=(label,target,event)
        with self._c() as c:
            c.execute('INSERT OR IGNORE INTO castle_daily_plans VALUES(?,?,?)',(uid,day,json.dumps(generated,ensure_ascii=False)))
            saved=c.execute('SELECT plan_json FROM castle_daily_plans WHERE user_id=? AND day=?',(uid,day)).fetchone()[0]
            c.commit()
        return {key:tuple(value) for key,value in json.loads(saved).items()}, {'tier':0,'label':'Classique · Tirage du jour','successes':0,
                             'gold':QUEST_GLOBAL_GOLD,'xp':QUEST_GLOBAL_XP}

    def _sync_daily_bonus(self,c,uid,day):
        row=c.execute('SELECT last_daily FROM castle_profiles WHERE user_id=?',(uid,)).fetchone()
        if row and (row['last_daily']==day or c.execute('SELECT 1 FROM castle_daily_receipts WHERE user_id=? AND day=?',(uid,day)).fetchone()):
            c.execute("INSERT INTO castle_daily_progress(user_id,day,quest_key,progress) VALUES(?,?, 'daily_bonus',1) ON CONFLICT(user_id,day,quest_key) DO UPDATE SET progress=MAX(progress,1)",(uid,day))

    def record(self,user_id,event,amount=1):
        self.ensure(user_id); uid=int(user_id); amount=max(0,int(amount)); day=self._today(); quest_cfg,_=self.quest_config(uid)
        col={'combat':'combats','arena_win':'wins','arena_loss':'losses','expedition':'expeditions','casino':'casino_games'}.get(event)
        xp={'arena_win':XP_REWARDS['arena_win'],'arena_loss':XP_REWARDS['arena_loss'],'casino':XP_REWARDS['casino']}.get(event,0) * event_multiplier(self.db_path,'xp_x2')
        with self._c() as c:
            c.execute('BEGIN IMMEDIATE')
            before_xp=int(c.execute('SELECT xp FROM castle_profiles WHERE user_id=?',(uid,)).fetchone()['xp'])
            if col: c.execute(f'UPDATE castle_profiles SET {col}={col}+?, xp=xp+? WHERE user_id=?',(amount,xp*amount,uid))
            elif xp: c.execute('UPDATE castle_profiles SET xp=xp+? WHERE user_id=?',(xp*amount,uid))
            after_xp=before_xp + xp*amount
            self._queue_levelups(c,uid,before_xp,after_xp)

            # Progression des quêtes basée sur l'événement réel.
            for key,(label,target,quest_event) in quest_cfg.items():
                inc = amount if quest_event == event else 0
                if inc:
                    c.execute('INSERT OR IGNORE INTO castle_daily_progress(user_id,day,quest_key) VALUES(?,?,?)',(uid,day,key))
                    c.execute('UPDATE castle_daily_progress SET progress=progress+? WHERE user_id=? AND day=? AND quest_key=?',(inc,uid,day,key))

            self._sync_level(c,uid)
            c.commit()
    def quests(self,user_id):
        self.ensure(user_id); uid=int(user_id); day=self._today(); out=[]; quest_cfg,meta=self.quest_config(uid)
        with self._c() as c:
            self._sync_daily_bonus(c,uid,day)
            already_claimed=bool(c.execute('SELECT 1 FROM castle_daily_progress WHERE user_id=? AND day=? AND claimed=1 LIMIT 1',(uid,day)).fetchone())
            for key,(label,target,event) in quest_cfg.items():
                c.execute('INSERT OR IGNORE INTO castle_daily_progress(user_id,day,quest_key) VALUES(?,?,?)',(uid,day,key))
            c.commit()
            rows={r['quest_key']:r for r in c.execute('SELECT * FROM castle_daily_progress WHERE user_id=? AND day=?',(uid,day))}
        for key,(label,target,event) in quest_cfg.items():
            r=rows[key]
            out.append({'key':key,'label':label,'target':target,'progress':min(int(r['progress']),target),'claimed':already_claimed or bool(r['claimed'])})
        return out,meta

    def claim_quests(self,user_id):
        """Récompense tout-ou-rien : toutes les quêtes proposées doivent être terminées."""
        uid=int(user_id); day=self._today(); quest_cfg,meta=self.quest_config(uid)
        with self._c() as c:
            c.execute('BEGIN IMMEDIATE')
            c.execute('INSERT OR IGNORE INTO castle_profiles(user_id) VALUES(?)',(uid,))
            self._sync_daily_bonus(c,uid,day)
            if c.execute('SELECT 1 FROM castle_daily_progress WHERE user_id=? AND day=? AND claimed=1 LIMIT 1',(uid,day)).fetchone():
                c.rollback(); return False,0,0,'claimed'
            rows=[]
            for key,(label,target,event) in quest_cfg.items():
                c.execute('INSERT OR IGNORE INTO castle_daily_progress(user_id,day,quest_key) VALUES(?,?,?)',(uid,day,key))
                r=c.execute('SELECT progress,claimed FROM castle_daily_progress WHERE user_id=? AND day=? AND quest_key=?',(uid,day,key)).fetchone()
                rows.append((key,target,int(r['progress']),bool(r['claimed'])))

            if all(claimed for _,_,_,claimed in rows):
                c.rollback(); return False,0,0,'claimed'
            if not all(progress >= target for _,target,progress,_ in rows):
                c.rollback(); return False,0,0,'incomplete'

            c.execute('UPDATE castle_daily_progress SET claimed=1 WHERE user_id=? AND day=?',(uid,day))
            c.execute('INSERT OR IGNORE INTO players(user_id) VALUES(?)',(uid,))
            gold_reward=int(meta['gold'])*event_multiplier(self.db_path,'gold_x2')
            xp_reward=int(meta['xp'])*event_multiplier(self.db_path,'xp_x2')
            c.execute('UPDATE players SET wallet_gold=wallet_gold+? WHERE user_id=?',(gold_reward,uid))
            before_xp=int(c.execute('SELECT xp FROM castle_profiles WHERE user_id=?',(uid,)).fetchone()['xp'])
            c.execute('UPDATE castle_profiles SET xp=xp+?, quests_completed=quests_completed+? WHERE user_id=?',(xp_reward,len(quest_cfg),uid))
            self._queue_levelups(c,uid,before_xp,before_xp+xp_reward)
            self._sync_level(c,uid)
            c.commit()
        return True,gold_reward,xp_reward,'ok'

    def claim_daily(self,user_id):
        uid=int(user_id); day=self._today(); self.ensure(uid)
        with self._c() as c:
            c.execute('BEGIN IMMEDIATE'); r=c.execute('SELECT last_daily FROM castle_profiles WHERE user_id=?',(uid,)).fetchone()
            if r and r['last_daily']==day: c.rollback(); return False,0
            if not c.execute('INSERT OR IGNORE INTO castle_daily_receipts(user_id,day) VALUES(?,?)',(uid,day)).rowcount:
                c.rollback(); return False,0
            c.execute('INSERT OR IGNORE INTO players(user_id) VALUES(?)',(uid,))
            gold_reward=DAILY_REWARD*event_multiplier(self.db_path,'gold_x2')
            xp_reward=DAILY_XP*event_multiplier(self.db_path,'xp_x2')
            c.execute('UPDATE players SET wallet_gold=wallet_gold+? WHERE user_id=?',(gold_reward,uid))
            before_xp=int(c.execute('SELECT xp FROM castle_profiles WHERE user_id=?',(uid,)).fetchone()['xp'])
            c.execute('UPDATE castle_profiles SET last_daily=?, xp=xp+? WHERE user_id=?',(day,xp_reward,uid))
            self._queue_levelups(c,uid,before_xp,before_xp+xp_reward)
            self._sync_level(c,uid); c.commit()
        return True,gold_reward
    def daily_available(self,user_id):
        uid=int(user_id);day=self._today()
        if self.profile(uid)['last_daily']==day:return False
        with self._c() as c:return not bool(c.execute('SELECT 1 FROM castle_daily_receipts WHERE user_id=? AND day=?',(uid,day)).fetchone())
    def leaderboard(self,limit=10):
        with self._c() as c:
            return [dict(r) for r in c.execute('SELECT user_id,wallet_gold,bank_gold,(wallet_gold+bank_gold) total FROM players ORDER BY total DESC,user_id ASC LIMIT ?',(int(limit),))]
