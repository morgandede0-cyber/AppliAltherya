"""Public probabilities describe the draw table, never a saved trip's hidden loot."""
from expedition_engine import LOOT_TABLES, EXPEDITIONS, BAG_LEVELS

def catalog():
    return {key:{tool:[dict(name=n,min_tier=t,weight=w) for n,t,w in table] for tool,table in tools.items()} for key,tools in LOOT_TABLES.items()}

def preparation(destination, tool, tier, bag_tier):
    zone=EXPEDITIONS.get(destination)
    if not zone or tool not in zone['tools']:
        raise ValueError('Cette destination ne correspond pas au métier.')
    table=[(n,t,w) for n,t,w in LOOT_TABLES.get(destination,{}).get(tool,[]) if t<=tier]
    total=sum(w for _,_,w in table)
    return dict(capacity=zone.get('capacity',6) if zone.get('barehand') else BAG_LEVELS[bag_tier]['capacity'],
                resources=[dict(name=n,chance=w/total) for n,_,w in table] if total else [])
