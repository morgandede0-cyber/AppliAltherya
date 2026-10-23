"""Bounded diagnostics: error class/status only, no URLs, tokens or payloads."""
import time
from aiohttp import web

def runtime_health(service):
 def record(code):
  try:
   with service().conn() as c:
    c.execute('INSERT INTO activity_runtime_errors(created_at,code) VALUES(?,?)',(time.time(),code))
    c.execute('DELETE FROM activity_runtime_errors WHERE id NOT IN(SELECT id FROM activity_runtime_errors ORDER BY id DESC LIMIT 100)')
  except Exception:pass # Diagnostics must never hide the original exception.
 @web.middleware
 async def middleware(request,handler):
  try:response=await handler(request)
  except web.HTTPException as e:
   if e.status>=500 and request.path.startswith('/api/'):record('HTTP '+str(e.status))
   raise
  except Exception as e:
   if request.path.startswith('/api/'):record(type(e).__name__[:80])
   raise
  if response.status>=500 and request.path.startswith('/api/'):record('HTTP '+str(response.status))
  return response
 return middleware
