"""Fixed-price player lots. Inventory, payment and closure share one transaction."""
import asyncio
import hashlib
import logging
import secrets
import time
import unicodedata
import re
from sqlite_store import atomic
from expedition_engine import RESOURCE_SELL_PRICES
from story_engine import ALL_STORY_ITEMS

ITEMS = tuple(sorted(set(RESOURCE_SELL_PRICES) - set(ALL_STORY_ITEMS)))
DURATION = 86400
MAX_ACTIVE = 20
MAX_GOLD = 1_000_000_000


def integer(value, low, high):
    if type(value) is not int or not low <= value <= high:
        raise ValueError('Quantité ou prix invalide.')
    return value


def profession(item):
    if re.search('Pierre|Minerai|Diamant|Cristal',item):return 'Mineur'
    if re.search('Viande|Peau|Croc|Griffe|Défense|Trophée',item):return 'Chasseur'
    if re.search('Bois|bois|Brindille',item):return 'Bûcheron'
    return 'Cueillette'

def folded(value):
    return ''.join(c for c in unicodedata.normalize('NFKD',value.casefold()) if not unicodedata.combining(c))

class Trading:
    def __init__(self, activity):
        self.a = activity
        with self.a.conn() as c:
            c.execute('''CREATE TABLE IF NOT EXISTS activity_trade_offers(
                id TEXT PRIMARY KEY, seller INTEGER NOT NULL, item TEXT NOT NULL,
                quantity INTEGER NOT NULL CHECK(quantity>0), price INTEGER NOT NULL CHECK(price>0),
                created_at REAL NOT NULL, expires_at REAL NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('active','sold','cancelled','expired')),
                buyer INTEGER, closed_at REAL)''')
            c.execute('CREATE INDEX IF NOT EXISTS trade_due ON activity_trade_offers(status,expires_at)')
            c.execute('CREATE INDEX IF NOT EXISTS trade_owner ON activity_trade_offers(seller,status)')

    def require(self, uid):
        if not self.a.discord_profile(uid):
            raise ValueError('Connexion Discord requise pour le commerce entre joueurs.')
        with self.a.conn() as c:
            canonical=c.execute('SELECT 1 FROM activity_discord_accounts WHERE user_id=?',(uid,)).fetchone()
        if not canonical:
            raise ValueError('Reconnectez votre compte Discord avant de commercer.')
        if not self.a.tutorial.state(uid)['completed']:
            raise ValueError('Terminez le tutoriel avant de commercer.')

    @staticmethod
    def credit(c, uid, item, quantity):
        c.execute('''INSERT INTO resources(user_id,resource_name,quantity) VALUES(?,?,?)
            ON CONFLICT(user_id,resource_name) DO UPDATE SET quantity=quantity+excluded.quantity''', (uid,item,quantity))

    def notify(self,c,row,kind):
        sold=kind=='sold';title='Lot vendu' if sold else 'Lot expiré'
        text=(f"{row['quantity']} × {row['item']} : {row['price']} Gold ont été crédités à votre portefeuille." if sold else f"{row['quantity']} × {row['item']} : vos objets ont été rendus à votre inventaire.")
        self.a.mailbox.send(c,[row['seller']],dict(title=title,text=text,gold=0,xp=0,pouciel=0,item='',quantity=0),'Comptoir des joueurs','trade:'+kind+':'+row['id'])

    def history(self,uid,page=0):
        self.require(uid)
        if type(page) is not int or not 0<=page<=100000:raise ValueError('Page invalide.')
        with atomic(self.a.path) as c:
            now=time.time();self.expire_in(c,now,uid)
            where="(o.seller=? OR o.buyer=?) AND o.status<>'active'"
            total=c.execute('SELECT COUNT(*) FROM activity_trade_offers o WHERE '+where,(uid,uid)).fetchone()[0];pages=max(1,(total+3)//4);page=min(page,pages-1)
            rows=c.execute('SELECT o.*,s.display_name seller_name,b.display_name buyer_name FROM activity_trade_offers o LEFT JOIN activity_discord s ON s.user_id=o.seller LEFT JOIN activity_discord b ON b.user_id=o.buyer WHERE '+where+' ORDER BY o.closed_at DESC,o.id DESC LIMIT 4 OFFSET ?',(uid,uid,page*4)).fetchall()
        return dict(entries=[dict(id=r['id'],item=r['item'],quantity=r['quantity'],price=r['price'],status=r['status'],mine=r['seller']==uid,seller_name=r['seller_name'] or 'Aventurier',buyer_name=r['buyer_name'] or '',closed_at=r['closed_at']) for r in rows],page=page,pages=pages,total=total,server_now=now,save_owner=hashlib.sha256(f'activity:{uid}'.encode()).hexdigest()[:24])

    def expire_in(self, c, now, uid=None):
        sql="SELECT * FROM activity_trade_offers WHERE status='active' AND expires_at<=?"
        rows=c.execute(sql + (' AND seller=?' if uid is not None else ''), (now,uid) if uid is not None else (now,)).fetchall()
        for row in rows:
            if c.execute("UPDATE activity_trade_offers SET status='expired',closed_at=? WHERE id=? AND status='active'", (now,row['id'])).rowcount:
                before=self.a.transaction_journal.capture(c,row['seller'])
                self.credit(c,row['seller'],row['item'],row['quantity'])
                self.notify(c,row,'expired')
                self.a.transaction_journal.record(c,row['seller'],row['seller'],'trade_expired','trade:expired:'+row['id'],before)
        return len(rows)

    def expire(self):
        now=time.time()
        with self.a.conn() as c:
            if not c.execute("SELECT 1 FROM activity_trade_offers WHERE status='active' AND expires_at<=? LIMIT 1",(now,)).fetchone():
                return 0
        with atomic(self.a.path) as c:
            return self.expire_in(c,now)

    def action(self, uid, body):
        self.require(uid)
        now=time.time()
        # Called exclusively inside Activity.action's BEGIN IMMEDIATE unit of work.
        with self.a.conn() as c:
            self.expire_in(c,now)
            action=body['action']
            if action=='trade_create':
                item=body.get('item')
                if not isinstance(item,str) or item not in ITEMS:
                    raise ValueError('Cet objet ne peut pas être mis en vente.')
                qty=integer(body.get('quantity'),1,1_000_000)
                price=integer(body.get('price'),1,MAX_GOLD)
                if c.execute("SELECT COUNT(*) FROM activity_trade_offers WHERE seller=? AND status='active'",(uid,)).fetchone()[0]>=MAX_ACTIVE:
                    raise ValueError('Vous avez déjà 20 lots en vente.')
                if not c.execute('UPDATE resources SET quantity=quantity-? WHERE user_id=? AND resource_name=? AND quantity>=?',(qty,uid,item,qty)).rowcount:
                    raise ValueError('Stock insuffisant : le lot n’a pas été publié.')
                c.execute("INSERT INTO activity_trade_offers VALUES(?,?,?,?,?,?,?,'active',NULL,NULL)",(secrets.token_urlsafe(18),uid,item,qty,price,now,now+DURATION))
                self.a.adventure.alert(c,uid,item)
                return 'Lot publié pour 24 h. Les objets ont été retirés de votre inventaire.'
            key=body.get('key')
            if not isinstance(key,str) or not 1<=len(key)<=64:
                raise ValueError('Annonce invalide.')
            row=c.execute('SELECT * FROM activity_trade_offers WHERE id=?',(key,)).fetchone()
            if not row or row['status']!='active':
                raise ValueError('Ce lot n’est plus disponible. Actualisez la liste.')
            if action=='trade_cancel':
                if row['seller']!=uid:
                    raise ValueError('Vous ne pouvez annuler que vos propres annonces.')
                c.execute("UPDATE activity_trade_offers SET status='cancelled',closed_at=? WHERE id=?",(now,key))
                self.credit(c,uid,row['item'],row['quantity'])
                return 'Annonce annulée. Le lot a été rendu à votre inventaire.'
            if action!='trade_buy':
                raise ValueError('Action de commerce invalide.')
            if row['seller']==uid:
                raise ValueError('Vous ne pouvez pas acheter votre propre lot.')
            if integer(body.get('price'),1,MAX_GOLD)!=row['price']:
                raise ValueError('Le prix confirmé ne correspond pas au lot.')
            price=row['price']
            if c.execute('SELECT wallet_gold FROM players WHERE user_id=?',(row['seller'],)).fetchone()[0]+price>MAX_GOLD:
                raise ValueError('Le portefeuille du vendeur est plein. Achat annulé.')
            if not c.execute('UPDATE players SET wallet_gold=wallet_gold-? WHERE user_id=? AND wallet_gold>=?',(price,uid,price)).rowcount:
                raise ValueError('Votre portefeuille ne contient pas assez de Gold.')
            c.execute('UPDATE players SET wallet_gold=wallet_gold+? WHERE user_id=?',(price,row['seller']))
            self.credit(c,uid,row['item'],row['quantity'])
            c.execute("UPDATE activity_trade_offers SET status='sold',buyer=?,closed_at=? WHERE id=?",(uid,now,key))
            self.notify(c,row,'sold')
            return f"Achat effectué : {row['quantity']} × {row['item']} pour {price} Gold."

    def listing(self, uid, mode='buy', page=0, search='', category='Tous', sort='ending'):
        self.require(uid)
        if mode not in ('buy','mine') or type(page) is not int or not 0<=page<=100000 or not isinstance(search,str) or len(search)>80:
            raise ValueError('Recherche invalide.')
        orders={'ending':'o.expires_at,o.id','price_asc':'o.price,o.expires_at,o.id','price_desc':'o.price DESC,o.expires_at,o.id','unit_asc':'CAST(o.price AS REAL)/o.quantity,o.expires_at,o.id'}
        if category not in ('Tous','Mineur','Chasseur','Bûcheron','Cueillette') or sort not in orders:raise ValueError('Filtre ou tri invalide.')
        with atomic(self.a.path) as c:
            now=time.time();self.expire_in(c,now)
            where="o.status='active'" + (' AND o.seller=?' if mode=='mine' else '')
            params=[uid] if mode=='mine' else []
            matches=[n for n in ITEMS if (category=='Tous' or profession(n)==category) and folded(search.strip()) in folded(n)]
            if not matches:where+=' AND 0'
            else:
                where+=' AND o.item IN ('+','.join('?' for _ in matches)+')';params.extend(matches)
            total=c.execute('SELECT COUNT(*) FROM activity_trade_offers o WHERE '+where,params).fetchone()[0]
            pages=max(1,(total+3)//4);page=min(page,pages-1)
            rows=c.execute('''SELECT o.*,d.display_name FROM activity_trade_offers o
                LEFT JOIN activity_discord d ON d.user_id=o.seller
                WHERE '''+where+
                ' ORDER BY '+orders[sort]+' LIMIT 4 OFFSET ?',(*params,page*4)).fetchall()
            offers=[dict(id=r['id'],seller_name=r['display_name'] or 'Aventurier',mine=r['seller']==uid,
                item=r['item'],quantity=r['quantity'],price=r['price'],created_at=r['created_at'],expires_at=r['expires_at']) for r in rows]
            stock=dict(c.execute('SELECT resource_name,quantity FROM resources WHERE user_id=? AND quantity>0',(uid,)).fetchall())
            return dict(offers=offers,total=total,page=page,pages=pages,server_now=now,
                inventory=[dict(item=k,quantity=stock[k]) for k in ITEMS if stock.get(k,0)>0],
                active_count=c.execute("SELECT COUNT(*) FROM activity_trade_offers WHERE seller=? AND status='active'",(uid,)).fetchone()[0],
                save_owner=hashlib.sha256(f'activity:{uid}'.encode()).hexdigest()[:24])


async def trade_lifecycle(app):
    service=app['discord_service_factory']()
    async def worker():
        while True:
            try:
                await asyncio.to_thread(service.trading.expire)
            except Exception:
                logging.getLogger(__name__).exception('Trade expiry failed; retrying next tick')
            await asyncio.sleep(1)
    task=asyncio.create_task(worker())
    try:
        yield
    finally:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
