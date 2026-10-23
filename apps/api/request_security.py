"""Bound expensive API calls before profile allocation or external OAuth calls."""
from collections import OrderedDict
import math
import time
from aiohttp import web


class RequestBudget:
    def __init__(self, clock=time.monotonic, maximum=4096):
        self.clock=clock
        self.maximum=maximum
        self.entries=OrderedDict()

    def take(self, key, capacity, refill):
        now=self.clock()
        tokens,previous=self.entries.pop(key,(float(capacity),now))
        tokens=min(capacity,tokens+max(0,now-previous)*refill)
        allowed=tokens>=1
        self.entries[key]=(tokens-1 if allowed else tokens,now)
        while len(self.entries)>self.maximum:
            self.entries.popitem(last=False)
        return 0 if allowed else max(1,math.ceil((1-tokens)/refill))


def api_security(service_factory, budget=None, *, anonymous_capacity=240, oauth_capacity=120):
    budget=budget if budget is not None else RequestBudget()

    @web.middleware
    async def protect(request, handler):
        if not request.path.startswith('/api/'):
            return await handler(request)
        if request.method=='POST':
            if request.headers.get('X-Altherya-Request')!='1' or request.headers.get('Sec-Fetch-Site')=='cross-site':
                raise web.HTTPForbidden(headers={'Cache-Control':'no-store'})
        # Forwarded headers and attacker-supplied cookie values never select buckets.
        remote=request.remote or 'unknown'
        if request.path=='/api/auth/discord':
            retry=budget.take(('oauth',remote),oauth_capacity,2)
        elif request.path in ('/api/activity','/api/admin','/api/avatar','/api/mail','/api/trade','/api/combat-history'):
            service=service_factory()
            uid=service.session_uid(request.cookies.get('altherya_test',''))
            verified=uid is not None and service.discord_profile(uid) is not None
            retry=budget.take(('player',uid),60,4) if verified else budget.take(('anonymous',remote),anonymous_capacity,4)
        else:
            retry=0
        if retry:
            return web.json_response({'error':'Trop de requêtes. Réessayez dans quelques secondes.'},status=429,headers={'Retry-After':str(retry),'Cache-Control':'no-store'})
        try:
            response=await handler(request)
        except web.HTTPException as error:
            error.headers.setdefault('Cache-Control','no-store')
            error.headers['X-Content-Type-Options']='nosniff'
            raise
        response.headers.setdefault('Cache-Control','no-store')
        response.headers['X-Content-Type-Options']='nosniff'
        return response

    return protect
