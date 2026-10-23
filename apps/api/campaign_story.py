"""Narrative consequences refer to recorded choices; no reward or gate changes."""
REACTIONS={
 'S1-Q04':('Le voleur se souvient du service de renseignement rendu : il vous a indiqué la piste des chargements.','Le voleur a reçu les 25 Gold annoncés. Son renseignement a permis de localiser le chargement.'),
 'S2-Q07':('Les convoyeurs secourus directement acceptent de témoigner en votre faveur. Leur récit devient une preuve humaine, au-delà des relevés.','Les renforts ont sécurisé la galerie : leurs observations donnent au château une chaîne de preuves vérifiable.'),
 'S3-Q04':('L’audition publique oblige le château à répondre ouvertement. Votre enquête est désormais connue des témoins.','Le vigile a transmis votre message discrètement. Vous pouvez suivre la piste sans annoncer votre prochain déplacement.'),
 'S3-Q05':('Votre enquête est publique : les témoins savent à qui remettre leurs informations, et le Faussaire sait que vous approchez.','Votre discrétion protège les témoins. Le dossier doit rester solidement étayé pour convaincre le château.'),
 'S4-Q03':('Le leurre attire le réseau sur une fausse piste. Lors de l’intervention, les gardes recherchent le signal convenu plutôt qu’un convoi réel.','Le barrage autorisé ferme les voies de fuite. L’intervention finale repose sur l’identification du convoi et les preuves réunies.'),
 'S4-Q07':('Le Faussaire a été sauvé et sera jugé. Les personnes secourues peuvent enfin confronter son récit aux preuves.','Les relevés ont été récupérés, mais le Faussaire a disparu. Le dossier matériel permet de poursuivre le réseau sans son témoignage.'),
}

def consequences(choices,quests):
    output=[]
    for key,value in choices.items():
        quest=next((q for q in quests if q['id']==key),None)
        step=next((s for s in quest['steps'] if s['kind']=='choice'),None) if quest else None
        if key in REACTIONS and step and value in step['options']:
            output.append(dict(quest_id=key,choice=value,reaction=REACTIONS[key][step['options'].index(value)]))
    return output

def enrich(quest,choices,quests):
    history=consequences(choices,quests)
    # Only earlier seasons and decisions in this season influence current dialogue.
    relevant=[r for r in history if r['quest_id']<quest['id']]
    return {**quest,'context':relevant[-1]['reaction'] if relevant else '', 'decision_history':history}

def playable_branch(quest,choices):
    """Edition 3 only. Accepted older quests keep their exact objectives."""
    import copy
    q=copy.deepcopy(quest);steps=q['steps'];extra=None
    if q['id']=='S2-Q08' and 'S2-Q07' in choices:
        direct=choices['S2-Q07']=='Secourir directement les convoyeurs'
        extra=dict(id='witness-account',kind='mission',label='Recueillir les témoignages des convoyeurs secourus' if direct else 'Faire authentifier les observations des renforts',place='Château de Legacy',duration=600 if direct else 900,text='Les témoins reconstituent les faits.' if direct else 'Les gardes recoupent les horaires et les relevés.')
    if q['id']=='S4-Q05' and 'S4-Q03' in choices:
        blockade=choices['S4-Q03']=='Préparer un barrage autorisé'
        steps[0]['label']='Faire fermer les voies de fuite avant l’interception' if blockade else 'Positionner le leurre et attendre le signal du réseau'
        steps[0]['duration']=4500 if blockade else 3900
        extra=dict(id='plan-check',kind='mission',label='Vérifier les postes du barrage' if blockade else 'Vérifier que les voyageurs ont quitté la route du leurre',place=steps[0].get('place','Route du convoi'),duration=600,text='Votre décision impose ces préparatifs avant toute intervention.')
    if extra:steps.insert(0,extra)
    return q
