import asyncio
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parents[1]))
from activity import Activity
from trading import DURATION, ITEMS, MAX_ACTIVE, trade_lifecycle


class TradeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.path=self.tmp.name+'/test.db';self.a=Activity(self.path)
        self.seller=self.make('123456789012345678','Panda du serveur')
        self.buyer=self.make('123456789012345679','Acheteur')
        self.other=self.make('123456789012345680','Autre')
        with self.a.conn() as c:
            c.execute('INSERT INTO resources VALUES(?,?,?)',(self.seller,'Pierre brute',100))
            c.execute('UPDATE players SET wallet_gold=1000')

    def tearDown(self):self.tmp.cleanup()

    def make(self,did,name,done=True):
        (uid,_),token=self.a.session('');self.a.snapshot(uid,name)
        self.a.bind_discord(uid,dict(id=did,username='Global',global_name=name,avatar=None,discriminator='0'),token)
        if done:
            for n in range(5):self.a.action(uid,dict(action='tutorial_next',step=n))
            self.a.action(uid,dict(action='tutorial_finish',step=5))
        return uid

    def stock(self,uid):
        with self.a.conn() as c:
            r=c.execute("SELECT quantity FROM resources WHERE user_id=? AND resource_name='Pierre brute'",(uid,)).fetchone()
            return r[0] if r else 0

    def offer(self,quantity=10,price=50,**extra):
        self.a.action(self.seller,dict(action='trade_create',item='Pierre brute',quantity=quantity,price=price,**extra))
        return self.a.trading.listing(self.seller,'mine')['offers'][-1]['id']

    def buy(self,key,uid=None,price=50,**extra):
        return self.a.action(uid or self.buyer,dict(action='trade_buy',key=key,price=price,**extra))

    def balance(self,uid):return self.a.economy.get_balance(uid).wallet

    def try_action(self,body,uid):
        try:self.a.action(uid,body);return True
        except ValueError:return False

    def due(self,key):
        with self.a.conn() as c:c.execute('UPDATE activity_trade_offers SET expires_at=0 WHERE id=?',(key,))

    def test_publish_reserves_real_stock_and_uses_server_duration(self):
        with patch('trading.time.time',return_value=123456):key=self.offer()
        self.assertEqual(self.stock(self.seller),90)
        with self.a.conn() as c:r=c.execute('SELECT * FROM activity_trade_offers WHERE id=?',(key,)).fetchone()
        self.assertEqual(r['expires_at']-r['created_at'],DURATION)
        # Stock is gone from the same resources table read by NPC sale and forge.
        self.assertEqual(self.a.expeditions.get_resources(self.seller)['Pierre brute'],90)

    def test_npc_cannot_sell_escrowed_stock_and_cancellation_returns_only_reserved_lot(self):
        key=self.offer(95)
        self.a.action(self.seller,dict(action='sell',key='Pierre brute',amount=6))
        self.assertEqual(self.stock(self.seller),5);self.assertEqual(self.balance(self.seller),1000)
        self.a.action(self.seller,dict(action='sell',key='Pierre brute',amount=5))
        self.assertEqual(self.stock(self.seller),0);self.assertEqual(self.balance(self.seller),1010)
        self.a.action(self.seller,dict(action='trade_cancel',key=key))
        self.assertEqual(self.stock(self.seller),95);self.assertEqual(self.balance(self.seller),1010)

    def test_sale_conserves_gold_and_delivers_entire_lot(self):
        key=self.offer();self.buy(key)
        self.assertEqual((self.stock(self.seller),self.stock(self.buyer)),(90,10))
        self.assertEqual((self.balance(self.seller),self.balance(self.buyer)),(1050,950))
        with self.assertRaises(ValueError):self.buy(key,self.other)
        self.assertEqual(self.stock(self.other),0)

    def test_concurrent_buyers_one_winner(self):
        key=self.offer()
        with ThreadPoolExecutor(2) as pool:
            results=list(pool.map(lambda uid:self.try_action(dict(action='trade_buy',key=key,price=50),uid),(self.buyer,self.other)))
        self.assertEqual(sum(results),1);self.assertEqual(self.stock(self.buyer)+self.stock(self.other),10)
        self.assertEqual(sum(self.balance(uid) for uid in (self.seller,self.buyer,self.other)),3000)

    def test_cancel_racing_buy_never_duplicates(self):
        key=self.offer()
        with ThreadPoolExecutor(2) as pool:
            fs=[pool.submit(self.try_action,dict(action='trade_cancel',key=key),self.seller),pool.submit(self.try_action,dict(action='trade_buy',key=key,price=50),self.buyer)]
            self.assertEqual(sum(f.result() for f in fs),1)
        self.assertEqual(self.stock(self.seller)+self.stock(self.buyer),100)
        self.assertEqual(self.balance(self.seller)+self.balance(self.buyer),2000)

    def test_cancel_only_owner_returns_exact_stock_once(self):
        key=self.offer()
        with self.assertRaises(ValueError):self.a.action(self.buyer,dict(action='trade_cancel',key=key))
        self.a.action(self.seller,dict(action='trade_cancel',key=key))
        with self.assertRaises(ValueError):self.a.action(self.seller,dict(action='trade_cancel',key=key))
        self.assertEqual(self.stock(self.seller),100)

    def test_expiry_boundary_and_repeated_workers(self):
        key=self.offer()
        with self.a.conn() as c:deadline=c.execute('SELECT expires_at FROM activity_trade_offers WHERE id=?',(key,)).fetchone()[0]
        with patch('trading.time.time',return_value=deadline-.001):self.assertEqual(self.a.trading.expire(),0)
        with patch('trading.time.time',return_value=deadline):
            with ThreadPoolExecutor(3) as pool:self.assertEqual(sum(pool.map(lambda _:self.a.trading.expire(),range(3))),1)
        self.assertEqual(self.stock(self.seller),100);self.assertEqual(self.a.trading.expire(),0)

    def test_restart_recovers_without_player_connection(self):
        key=self.offer();self.due(key);a=Activity(self.path);self.assertEqual(a.trading.expire(),1);self.assertEqual(self.stock(self.seller),100)

    def test_snapshot_also_returns_expired_lot(self):
        key=self.offer();self.due(key);self.a.snapshot(self.seller,'Panda');self.assertEqual(self.stock(self.seller),100)

    def test_expired_offer_cannot_be_bought_even_before_worker(self):
        key=self.offer();self.due(key)
        with self.assertRaises(ValueError):self.buy(key)
        self.a.trading.expire();self.assertEqual(self.stock(self.seller),100);self.assertEqual(self.balance(self.buyer),1000)

    def test_full_seller_wallet_does_not_lose_buyers_payment(self):
        key=self.offer()
        with self.a.conn() as c:c.execute('UPDATE players SET wallet_gold=1000000000 WHERE user_id=?',(self.seller,))
        with self.assertRaises(ValueError):self.buy(key)
        self.assertEqual(self.stock(self.buyer),0);self.assertEqual(self.balance(self.buyer),1000)
        self.a.action(self.seller,dict(action='trade_cancel',key=key));self.assertEqual(self.stock(self.seller),100)

    def test_insufficient_gold_or_wrong_price_rolls_back_everything(self):
        key=self.offer(price=1001)
        for price in (1001,1,True,None):
            with self.assertRaises(ValueError):self.buy(key,price=price)
        self.assertEqual(self.balance(self.buyer),1000);self.assertEqual(self.stock(self.buyer),0)
        self.assertEqual(len(self.a.trading.listing(self.seller,'mine')['offers']),1)

    def test_self_buy_and_foreign_cancel_rejected(self):
        key=self.offer()
        with self.assertRaises(ValueError):self.buy(key,self.seller)
        self.assertEqual(self.stock(self.seller),90);self.assertEqual(self.balance(self.seller),1000)

    def test_invalid_items_and_numeric_types(self):
        for item in ('Clé des ombres','Technique','<script>','Pierre brute\x00',None,[]):
            with self.subTest(item=item),self.assertRaises(ValueError):self.a.action(self.seller,dict(action='trade_create',item=item,quantity=1,price=1))
        for value in (-1,0,1.5,True,'5',None,10**15):
            for field in ('quantity','price'):
                body=dict(action='trade_create',item='Pierre brute',quantity=1,price=1);body[field]=value
                with self.subTest(field=field,value=value),self.assertRaises(ValueError):self.a.action(self.seller,body)
        self.assertEqual(self.stock(self.seller),100)

    def test_multiple_lots_cannot_exceed_inventory(self):
        self.offer(80)
        with self.assertRaises(ValueError):self.offer(21)
        self.assertEqual(self.stock(self.seller),20)

    def test_active_listing_cap(self):
        for _ in range(MAX_ACTIVE):self.offer(1)
        with self.assertRaises(ValueError):self.offer(1)
        self.assertEqual(self.stock(self.seller),80)

    def test_idempotent_publish_and_purchase(self):
        body=dict(action='trade_create',item='Pierre brute',quantity=10,price=50,request_id='trade-create-test-123')
        self.a.action(self.seller,body);self.a.action(self.seller,body);self.assertEqual(self.stock(self.seller),90)
        key=self.a.trading.listing(self.seller,'mine')['offers'][0]['id']
        self.buy(key,request_id='trade-buy-test-1234');self.buy(key,request_id='trade-buy-test-1234')
        self.assertEqual(self.balance(self.buyer),950);self.assertEqual(self.stock(self.buyer),10)

    def test_failure_after_payment_rolls_back(self):
        key=self.offer()
        with patch.object(self.a.trading,'credit',side_effect=RuntimeError('Disk failure')):
            with self.assertRaises(RuntimeError):self.buy(key)
        self.assertEqual((self.balance(self.seller),self.balance(self.buyer)),(1000,1000));self.assertEqual(self.stock(self.buyer),0)
        self.buy(key);self.assertEqual(self.stock(self.buyer),10)

    def test_discord_and_tutorial_required(self):
        (uid,_),_=self.a.session('');self.a.snapshot(uid,'Guest')
        with self.assertRaises(ValueError):self.a.trading.listing(uid)
        uid=self.make('123456789012345681','Novice',False)
        with self.assertRaises(ValueError):self.a.trading.listing(uid)

    def test_listing_privacy_pagination_server_names_and_literal_search(self):
        self.offer();data=self.a.trading.listing(self.buyer)
        self.assertEqual(data['offers'][0]['seller_name'],'Panda du serveur')
        self.assertFalse(data['offers'][0]['mine']);self.assertNotIn('seller',data['offers'][0]);self.assertNotIn('discord_id',str(data))
        self.assertEqual(self.a.trading.listing(self.buyer,'mine')['total'],0)
        self.assertEqual(self.a.trading.listing(self.buyer,search="%' OR 1=1 --")['total'],0)
        for _ in range(5):self.offer(1)
        self.assertEqual(len(self.a.trading.listing(self.buyer)['offers']),4)
        self.assertEqual(len(self.a.trading.listing(self.buyer,page=1)['offers']),2)
        self.assertEqual(data['inventory'],[])

    def test_maintenance_blocks_trade_but_automatic_refund_continues(self):
        key=self.offer()
        with self.a.conn() as c:c.execute('INSERT INTO activity_maintenance VALUES(?,?,?,?,?)',('trade','Tests',0,'admin',0))
        with self.assertRaises(ValueError):self.buy(key)
        self.due(key);self.assertEqual(self.a.trading.expire(),1);self.assertEqual(self.stock(self.seller),100)

    def test_refunds_do_not_fail_when_inventory_has_grown(self):
        key=self.offer()
        with self.a.conn() as c:c.execute('UPDATE resources SET quantity=1000000000 WHERE user_id=?',(self.seller,))
        self.due(key);self.a.trading.expire();self.assertEqual(self.stock(self.seller),1000000010)

    def test_failed_expiry_is_retryable(self):
        key=self.offer();self.due(key)
        with patch.object(self.a.trading,'credit',side_effect=RuntimeError('Disk failure')):
            with self.assertRaises(RuntimeError):self.a.trading.expire()
        self.assertEqual(self.stock(self.seller),90);self.a.trading.expire();self.assertEqual(self.stock(self.seller),100)

    def test_multiple_sessions_do_not_duplicate_market_rows(self):
        key=self.offer()
        (uid,_),token=self.a.session('')
        self.a.bind_discord(uid,dict(id='123456789012345678',username='Global',global_name='Panda du serveur',avatar=None,discriminator='0'),token)
        data=self.a.trading.listing(self.buyer)
        self.assertEqual(data['total'],1);self.assertEqual([r['id'] for r in data['offers']],[key])

    def test_whitelist_excludes_story(self):
        from story_engine import ALL_STORY_ITEMS
        self.assertFalse(set(ITEMS)&set(ALL_STORY_ITEMS))

    def test_lifecycle_returns_without_any_player_request(self):
        key=self.offer();self.due(key)
        async def run():
            context=trade_lifecycle({'discord_service_factory':lambda:self.a});await anext(context)
            for _ in range(30):
                if self.stock(self.seller)==100:break
                await asyncio.sleep(.02)
            await context.aclose()
        asyncio.run(run());self.assertEqual(self.stock(self.seller),100)


class TradeHttpTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        from aiohttp import web
        from aiohttp.test_utils import TestClient,TestServer
        from request_security import api_security
        import activity as adapter
        import server
        self.tmp=tempfile.TemporaryDirectory();self.a=Activity(self.tmp.name+'/test.db');self.old=adapter.SERVICE;adapter.SERVICE=self.a
        app=web.Application(middlewares=[api_security(lambda:self.a)])
        app.router.add_get('/api/trade',server.trade);app.router.add_post('/api/activity',adapter.activity)
        self.client=TestClient(TestServer(app));await self.client.start_server()

    async def asyncTearDown(self):
        import activity as adapter
        await self.client.close();adapter.SERVICE=self.old;self.tmp.cleanup()

    async def test_unauthenticated_listing_allocates_no_profile(self):
        response=await self.client.get('/api/trade');self.assertEqual(response.status,403)
        with self.a.conn() as c:self.assertEqual(c.execute('SELECT COUNT(*) FROM activity_sessions').fetchone()[0],0)

    async def test_csrf_and_verified_listing_validation(self):
        (uid,name),token=self.a.session('');self.a.snapshot(uid,name)
        self.a.bind_discord(uid,dict(id='123456789012345678',username='Test',global_name='Test',avatar=None,discriminator='0'),token)
        self.client.session.cookie_jar.update_cookies({'altherya_test':token})
        self.assertEqual((await self.client.get('/api/trade')).status,400)
        for n in range(5):self.a.action(uid,dict(action='tutorial_next',step=n))
        self.a.action(uid,dict(action='tutorial_finish',step=5))
        response=await self.client.get('/api/trade');self.assertEqual(response.status,200);self.assertEqual(response.headers['Cache-Control'],'no-store')
        data=await response.json();self.assertEqual(data['offers'],[])
        for query in ('?mode=invalid','?page=-1','?page=nan','?search='+'a'*81):self.assertEqual((await self.client.get('/api/trade'+query)).status,400)
        body=dict(action='trade_create',item='Pierre brute',quantity=1,price=1)
        self.assertEqual((await self.client.post('/api/activity',json=body)).status,403)
        self.assertEqual((await self.client.post('/api/activity',json=body,headers={'X-Altherya-Request':'1','Sec-Fetch-Site':'cross-site'})).status,403)
