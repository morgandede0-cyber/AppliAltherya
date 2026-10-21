"""Private slash commands on the Activity gateway, sharing the same admin engine."""
import json,os
import discord
from discord.http import Route
from activity_admin import DEFAULT_ADMIN_IDS
NAME='altherya-admin'
def option(name,description,kind=3,required=True):return dict(name=name,description=description,type=kind,required=required)
COMMAND=dict(name=NAME,description='Administration privée d’Altherya',type=1,contexts=[0],integration_types=[0],options=[
 dict(name='aide',description='Lister les commandes de gestion',type=1),
 dict(name='etat',description='État des maintenances',type=1),
 dict(name='maintenance',description='Fermer ou rouvrir le jeu ou un lieu',type=1,options=[option('lieu','global, bank, arena, tower… /aide donne la liste'),option('active','Activer le verrouillage',5),option('motif','Message affiché aux joueurs'),option('minutes','0 pour durée illimitée',4,False)]),
 dict(name='joueur',description='Préparer une commande pour un joueur',type=1,options=[option('cible','Joueur Discord',6),option('commande','Identifiant donné par /aide'),option('motif','Motif de la modification'),option('valeur','Valeur numérique',4,False),option('cle','Objet, technique ou emplacement',3,False),option('active','Choix oui/non',5,False),option('voie','Voie de l’armure',3,False),option('qualite','Qualité de l’armure',3,False)]),
 dict(name='royaume',description='Préparer une commande globale',type=1,options=[option('commande','announcement, gift_gold ou event'),option('motif','Motif obligatoire'),option('valeur','Gold par joueur',4,False),option('texte','Texte de service (vide pour retirer)',3,False),option('cle','gold_x2 ou xp_x2',3,False),option('active','Activer le bonus',5,False)])])

def actor(service,discord_id):
 ids={x.strip() for x in os.environ['ACTIVITY_ADMIN_IDS'].split(',')} if 'ACTIVITY_ADMIN_IDS' in os.environ else DEFAULT_ADMIN_IDS
 if str(discord_id) not in ids:raise PermissionError('Accès administrateur refusé.')
 with service.conn() as c:row=c.execute('SELECT user_id FROM activity_discord_accounts WHERE discord_id=?',(str(discord_id),)).fetchone()
 if not row:raise ValueError('Connectez-vous une première fois à l’Activity avec votre compte Discord.')
 service.admin.require(row[0]);return row[0]

class ConfirmCommand(discord.ui.View):
 def __init__(self,service,owner,token):
  super().__init__(timeout=300);self.service=service;self.owner=owner;self.token=token
 @discord.ui.button(label='Confirmer',style=discord.ButtonStyle.danger)
 async def confirm(self,interaction,button):
  if interaction.user.id!=self.owner:return await interaction.response.send_message('Cette confirmation ne vous appartient pas.',ephemeral=True)
  await interaction.response.defer(ephemeral=True)
  try:
   uid=actor(self.service,interaction.user.id);result=self.service.admin_commands.confirm(uid,self.token)
   await interaction.edit_original_response(content=result['message'],view=None);self.stop()
  except (ValueError,PermissionError) as e:await interaction.followup.send(str(e),ephemeral=True,allowed_mentions=discord.AllowedMentions.none())
 @discord.ui.button(label='Annuler',style=discord.ButtonStyle.secondary)
 async def cancel(self,interaction,button):
  if interaction.user.id!=self.owner:return await interaction.response.send_message('Cette confirmation ne vous appartient pas.',ephemeral=True)
  try:self.service.admin_commands.cancel(actor(self.service,interaction.user.id),self.token)
  except (ValueError,PermissionError):return await interaction.response.send_message('Annulation refusée.',ephemeral=True)
  await interaction.response.edit_message(content='Commande annulée.',view=None);self.stop()

async def register(client):
 await client.http.request(Route('POST','/applications/{application_id}/commands',application_id=int(client.portal_application)),json=COMMAND)

async def handle(client,interaction):
 service=client.store.service
 try:
  if not client.validated or str(interaction.application_id)!=client.portal_application:raise PermissionError('Application Discord incorrecte.')
  expected=os.getenv('DISCORD_GUILD_ID','').strip()
  if expected and str(interaction.guild_id)!=expected:raise PermissionError('Serveur Discord incorrect.')
  if not interaction.guild_id:raise PermissionError('Commande réservée au serveur.')
  uid=actor(service,interaction.user.id)
  sub=(interaction.data.get('options') or [{}])[0];kind=sub.get('name');values={o['name']:o['value'] for o in sub.get('options',[])}
  await interaction.response.defer(ephemeral=True)
  if kind=='aide':
   catalogue=service.admin_commands.catalogue();text='\n'.join(c['id']+' · '+c['label'] for c in catalogue['commands'])+'\n\nLieux :\n'+'\n'.join(k+' · '+v for k,v in catalogue['maintenance']['places'].items())
   import io
   await interaction.followup.send('Catalogue complet des commandes. Chaque modification demande une confirmation et un motif.',file=discord.File(io.BytesIO(text.encode()),filename='commandes-admin.txt'),ephemeral=True);return
  if kind=='etat':
   data=service.maintenance.public();text='\n'.join(data['places'][r['scope']]+' : '+r['message'] for r in data['closures']) or 'Tous les lieux sont ouverts.'
   await interaction.followup.send(text[:1900],ephemeral=True,allowed_mentions=discord.AllowedMentions.none());return
  if kind=='maintenance':body=dict(command='maintenance',args={'key':values.get('lieu'),'enabled':values.get('active'),'value':values.get('minutes',0)},reason=values.get('motif'))
  else:
   cmd=next((c for c in service.admin_commands.catalogue()['commands'] if c['id']==values.get('commande')),None)
   if not cmd or cmd['scope']!=('player' if kind=='joueur' else 'game'):raise ValueError('Commande incorrecte pour ce groupe. Consultez /altherya-admin aide.')
   mapping={'value':'valeur','key':'cle','enabled':'active','branch':'voie','tier':'qualite','text':'texte'}
   args={a['name']:values.get(mapping[a['name']],'' if a['type']=='text' else None) for a in cmd['args']}
   body=dict(command=cmd['id'],args=args,reason=values.get('motif'),player=str(values.get('cible','')))
  preview=service.admin_commands.preview(uid,body)
  text=f"**{preview['label']}**\nCible : {preview.get('player') or 'Royaume'}\nParamètres : {json.dumps(body['args'],ensure_ascii=False)}\nMotif : {body['reason']}\nCibles concernées : {preview['affected']}\nConfirmez sous cinq minutes."
  await interaction.followup.send(text[:1900],view=ConfirmCommand(service,interaction.user.id,preview['token']),ephemeral=True,allowed_mentions=discord.AllowedMentions.none())
 except (PermissionError,ValueError) as e:
  if interaction.response.is_done():await interaction.followup.send(str(e),ephemeral=True,allowed_mentions=discord.AllowedMentions.none())
  else:await interaction.response.send_message(str(e),ephemeral=True,allowed_mentions=discord.AllowedMentions.none())
