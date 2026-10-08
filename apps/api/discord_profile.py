"""Verified OAuth profile metadata for the existing isolated Activity session."""
import re,hashlib

def verified_user(user):
    if not isinstance(user,dict):raise ValueError('Profil Discord invalide')
    uid=user.get('id','');avatar=user.get('avatar');username=user.get('username');display=user.get('global_name') or username;discriminator=str(user.get('discriminator','0'))
    if not isinstance(uid,str) or not re.fullmatch(r'[0-9]{1,22}',uid):raise ValueError('Identifiant Discord invalide')
    if avatar is not None and (not isinstance(avatar,str) or not re.fullmatch(r'(?:a_)?[a-f0-9]{32}',avatar)):raise ValueError('Avatar Discord invalide')
    if not isinstance(username,str) or not 1<=len(username)<=64 or not isinstance(display,str) or not 1<=len(display)<=64 or not re.fullmatch(r'[0-9]{1,4}',discriminator):raise ValueError('Nom Discord invalide')
    return dict(discord_id=uid,avatar=avatar or '',username=username,display_name=display,discriminator=discriminator)

def avatar_cdn(profile):
    # URL constructed exclusively from the verified Discord response, never a client URL.
    if profile['avatar']:return f"https://cdn.discordapp.com/avatars/{profile['discord_id']}/{profile['avatar']}.png?size=256"
    index=(int(profile['discord_id'])>>22)%6 if int(profile['discriminator'])==0 else int(profile['discriminator'])%5
    return f'https://cdn.discordapp.com/embed/avatars/{index}.png'

def avatar_revision(profile):
    return hashlib.sha256((profile['discord_id']+':'+profile['avatar']+':'+profile['discriminator']).encode()).hexdigest()[:16]
