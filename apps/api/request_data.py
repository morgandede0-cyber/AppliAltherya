"""Bound JSON structure before it reaches game or administration handlers."""
import math

async def object_body(request):
    try:
        body=await request.json()
    except (ValueError,TypeError,RecursionError,OverflowError) as error:
        raise ValueError('Requête JSON invalide.') from error
    if not isinstance(body,dict):
        raise ValueError('Requête JSON invalide.')
    pending=[(body,0)]
    while pending:
        value,depth=pending.pop()
        if depth>32 or isinstance(value,float) and not math.isfinite(value):
            raise ValueError('Structure JSON invalide ou trop profonde.')
        if isinstance(value,dict):pending.extend((v,depth+1) for v in value.values())
        elif isinstance(value,list):pending.extend((v,depth+1) for v in value)
    return body
