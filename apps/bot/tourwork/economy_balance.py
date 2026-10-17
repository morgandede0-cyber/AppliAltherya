"""Gold scale shared by the Activity's displays and authoritative engines."""
BALANCE_VERSION = '20261017-economy-v1'
DAILY_GOLD = 10
DAILY_QUEST_GOLD = 30
STARTER_PRICES = {'pickaxe': 400, 'axe': 400, 'spear': 400, 'bag': 400}
FORGE_COSTS = {'tool': {2: 150, 3: 350, 4: 700, 5: 1400},
               'bag': {2: 200, 3: 450, 4: 900, 5: 1800}}
JOB_GOLD = {'common': (8, 12), 'uncommon': (12, 18), 'rare': (18, 28),
            'epic': (28, 40), 'legendary': (40, 60)}

def story_price(group):
    return 30 + 5 * (int(group) - 1)
