import unittest,importlib.util,os
from pathlib import Path
from unittest.mock import patch
from aiohttp import web
spec=importlib.util.spec_from_file_location('gateway',Path(__file__).parents[1]/'server.py');gateway=importlib.util.module_from_spec(spec);spec.loader.exec_module(gateway)
class Request:
    def __init__(self,path=''):self.match_info={'path':path}
class GatewayTests(unittest.IsolatedAsyncioTestCase):
    async def test_health(self):self.assertEqual((await gateway.health(Request())).status,200)
    async def test_oauth_unconfigured_closed(self):
        with patch.dict(os.environ,{'DISCORD_CLIENT_ID':'','DISCORD_CLIENT_SECRET':''}):self.assertEqual((await gateway.auth(Request())).status,503)
    async def test_static_traversal_blocked(self):
        with self.assertRaises(web.HTTPNotFound):await gateway.static(Request('../../api/server.py'))
    async def test_static_index(self):self.assertEqual((await gateway.static(Request())).status,200)
if __name__=='__main__':unittest.main()
