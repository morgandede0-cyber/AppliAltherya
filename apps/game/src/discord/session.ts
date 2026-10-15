import {DiscordSDK} from '@discord/embedded-app-sdk';
import {isDiscordActivity,connectionError} from './context';
let sdk:DiscordSDK|undefined,inFlight:ReturnType<typeof authenticate>|undefined;
function timeout<T>(work:Promise<T>,label:string):Promise<T>{let timer:ReturnType<typeof setTimeout>;return Promise.race([work,new Promise<T>((_,reject)=>{timer=setTimeout(()=>reject(new Error(label+' : délai dépassé. Fermez puis relancez l’activité.')),25000);})]).finally(()=>clearTimeout(timer));}
export type AuthStage='ready'|'authorize'|'server'|'authenticate';
async function authenticate(onStage?:(stage:AuthStage)=>void){
 const id=import.meta.env.VITE_DISCORD_CLIENT_ID?.trim();if(!id||!/^\d{15,22}$/.test(id))throw new Error('VITE_DISCORD_CLIENT_ID absent ou invalide lors de la construction.');
 sdk??=new DiscordSDK(id);let stage='Initialisation Discord';
 try{
  onStage?.('ready');await timeout(sdk.ready(),stage);stage='Autorisation Discord';
  onStage?.('authorize');const {code}=await timeout(sdk.commands.authorize({client_id:id,response_type:'code',state:'',prompt:'none',scope:['identify']}),stage);
  onStage?.('server');stage='Vérification du compte par le serveur';const res=await timeout(fetch('/api/auth/discord',{method:'POST',credentials:'include',headers:{'Content-Type':'application/json','X-Altherya-Request':'1'},body:JSON.stringify({code})}),stage);
  const data=await res.json();if(!res.ok)throw new Error(typeof data.error==='string'?data.error:'Connexion Discord refusée par le serveur.');
  if(typeof data.access_token!=='string')throw new Error('Réponse de connexion invalide.');
  onStage?.('authenticate');stage='Authentification Discord';const auth=await timeout(sdk.commands.authenticate({access_token:data.access_token}),stage);return {sdk,user:auth.user};
 }catch(error){throw new Error(stage+' : '+connectionError(error));}
}
export async function connect(onStage?:(stage:AuthStage)=>void){if(!isDiscordActivity())return null;inFlight??=authenticate(onStage).finally(()=>{inFlight=undefined;});return inFlight;}
