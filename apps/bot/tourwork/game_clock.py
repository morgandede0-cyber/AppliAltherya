"""One civil day for game limits, independent of the host timezone."""
import time
from datetime import datetime,timedelta
from zoneinfo import ZoneInfo
ZONE=ZoneInfo('Europe/Paris')

def local_date(timestamp=None):
    return datetime.fromtimestamp(time.time() if timestamp is None else timestamp,ZONE).date()

def today():return local_date().isoformat()

def next_midnight(timestamp=None):
    stamp=time.time() if timestamp is None else timestamp
    return datetime.combine(local_date(stamp)+timedelta(days=1),datetime.min.time(),ZONE).timestamp()

def seconds_until_midnight():
    stamp=time.time()
    return max(0,int(next_midnight(stamp)-stamp))
