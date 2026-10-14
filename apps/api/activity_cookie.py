"""One cookie contract for the Discord iframe and direct localhost tests."""
import os
from urllib.parse import urlsplit

def set_activity_cookie(response,request,token):
 if not token:return
 configured=bool(os.getenv('DISCORD_CLIENT_ID','').strip() and os.getenv('DISCORD_CLIENT_SECRET','').strip())
 hostname=urlsplit('//'+request.host).hostname
 local=hostname in ('localhost','127.0.0.1','::1') and not request.secure and request.headers.get('X-Forwarded-Proto','').split(',')[0].strip()!='https'
 partitioned=configured and not local
 response.set_cookie('altherya_test',token,path='/',httponly=True,samesite='None' if partitioned else 'Strict',secure=partitioned or request.secure,max_age=31536000)
 if partitioned:
  # Python 3.12's Morsel lacks the Partitioned attribute. Serialize this cookie
  # ourselves rather than depending on a newer Python/aiohttp runtime.
  value=response.cookies['altherya_test'].OutputString()+'; Partitioned'
  del response.cookies['altherya_test']
  response.headers.add('Set-Cookie',value)
 # No Domain attribute: the browser binds it to the actual response host,
 # including {application_id}.discordsays.com behind Discord's proxy.
