"""Read-only guidance derived from the same snapshot and gates as gameplay."""
def objectives(s):
    result=[]
    def add(key,title,detail,route,current=0,target=1,ready=False):
        result.append(dict(key=key,title=title,detail=detail,route=route,current=current,target=target,ready=ready))
    if not s['tutorial']['completed']:
        add('tutorial','Terminer votre accueil','La récompense de départ contribue à vos premiers achats.','tutorial')
        return result
    if s['pending'] and s['pending']['ready']:
        add('contract','Récupérer votre contrat',f"{s['pending']['job']['reward']} Gold vous attendent.",'jobs',1,1,True)
    qs=s['quests']
    if qs and all(q['progress']>=q['target'] and not q['claimed'] for q in qs):
        add('daily','Réclamer les quotidiennes',f"{s['quest_reward']['gold']} Gold · {s['quest_reward']['xp']} XP",'castle',1,1,True)
    c=s['campaign'];q=c.get('quest')
    if q:
        if not c['level_allowed']:
            add('campaign-level',f"Atteindre le niveau {q['min_level']}",'Contrats, expéditions et arène donnent de l’XP pour poursuivre l’histoire.','journal',s['level'],q['min_level'])
        elif not c['accepted']:
            add('campaign','Accepter votre prochaine quête',q['title'],'campaign')
        elif c['stage']>=len(q['steps']):
            add('campaign','Remettre votre quête',f"{q['gold']} Gold · {q['xp']} XP",'campaign',1,1,True)
        else:
            step=q['steps'][c['stage']]
            detail=step.get('place') or q['giver']
            if c.get('deadline',0)>s['server_now']:detail+=' · Rapport dans '+str(max(1,int((c['deadline']-s['server_now']+59)//60)))+' min.'
            add('campaign',step['label'],detail,'campaign',c['stage'],len(q['steps']))
    tools=[k for k in ('axe','pickaxe','spear') if s['owned'].get(k)]
    if not tools or not s['owned'].get('bag'):
        price=(min(s['catalog'][k]['price'] for k in ('axe','pickaxe','spear')) if not tools else 0)+(0 if s['owned'].get('bag') else s['catalog']['bag']['price'])
        have=s['balance']['wallet']
        add('equipment','Préparer votre premier métier',f"Un outil et un sac : {price} Gold encore à acheter. "+('Équipement abordable au marché.' if have>=price else 'Contrats et cueillette permettent d’économiser.'),'market:buy',min(have,price),price,have>=price)
    # Only the next available tool upgrade; materials and Gold are explicit.
    else:
        key=min(tools,key=lambda k:s['gear'][k+'_level']);tier=s['gear'][key+'_level']+1
        if tier in s['forge_levels']:
            level=s['forge_levels'][tier];cost=s['forge_gold']['tool'][tier]
            missing=[f"{max(0,qty-s['resources'].get(name,0))} {name}" for name,qty in s['recipes'][tier].items() if s['resources'].get(name,0)<qty]
            ready=s['level']>=level and s['balance']['wallet']>=cost and not missing
            detail=f"Niveau {level} · {cost} Gold. "+('Matériaux prêts.' if not missing else 'À réunir : '+', '.join(missing))
            add('forge',f"Améliorer : {s['catalog'][key]['name'].split(' en ')[0]}",detail,'forge',s['level'] if s['level']<level else level,level,ready)
    destinations=[(key,d) for key,d in s['destinations'].items() if d['level']>s['level']]
    if destinations:
        key,d=min(destinations,key=lambda item:item[1]['level'])
        add('destination','Prochain lieu : '+d['name'],f"Accès au niveau {d['level']} ; équipement requis à préparer.",'world',s['level'],d['level'])
    add('level',f"Prochain niveau : {s['level']+1}",f"Encore {s['xp_needed']-s['xp']} XP à gagner.",'journal',s['xp'],s['xp_needed'])
    return result
