export type ArenaFighter={name:string;hp:number;max_hp:number;ultimate_cd:number;statuses?:{key:string;label:string}[]};
export type ArenaChampion={level:number;name:string;role:string;emblem:string;color:string;style:string;hint:string;phases:number};
export type ArenaEvent={id:number;round:number;actor:number;target:number;action:string;skill:string;damage:number;bleed:number;critical:boolean;guarded:boolean;kind:string;text:string};
export type ArenaStat={damage:number;hits:number;misses:number;critical:number;guards:number};
export type ArenaResult={battle_id:string;won:boolean;abandoned:boolean;champion:ArenaChampion;wager:number;payout:number;net_gold:number;xp:number;rating_before:number;rating_after:number;rating_delta:number;wins_before:number;wins_after:number;next_champion:ArenaChampion;circuit_complete:boolean;rounds:number;duration:number;stats:ArenaStat[];fighters?:ArenaFighter[];events?:ArenaEvent[];logs?:string[];skills?:Record<string,{name:string;power?:number;accuracy?:number;emoji?:string}>;hp:number;max_hp:number};
export type Objective={key:string;title:string;detail:string;route:string;current:number;target:number;ready:boolean};
export type CampaignStep={id:string;label:string;kind:string;place?:string;scene_image?:string;text?:string;duration?:number;question?:string;options?:string[];resource?:string;quantity?:number;destination?:string;enemy?:string};
export type CampaignState={complete:boolean;title:string;completed:number;total:number;revision:number;accepted?:boolean;level_allowed?:boolean;stage:number;deadline:number;retry_at:number;claim_at:number;expedition_ready?:boolean;choices:Record<string,string>;quest?:{id:string;season:number;chapter:number;title:string;giver:string;locations:string;scene:string;dialogue:string;resolution:string;min_level:number;difficulty:number;gold:number;xp:number;steps:CampaignStep[]};battle?:null|{fighters:{name:string;hp:number;max_hp:number}[];log:string[];finished:boolean;won:boolean|null;turn:number;ultimate_cd:number}};
export type Card={rank?:string;suit?:string;hidden?:boolean};
export type PlayState={champion?:ArenaChampion;round?:number;phase?:number;events?:ArenaEvent[];combat_stats?:ArenaStat[];intent?:{key:string;name:string};result?:ArenaResult;skills?:Record<string,{name:string;power?:number;accuracy?:number;emoji?:string}>;revision:number;kind?:string;status?:string;outcome?:'victory'|'defeat';message?:string;wager?:number;payout?:number;player?:Card[]|string|number;dealer?:Card[];player_total?:number;dealer_total?:number;opponent?:string|number;reels?:string[];number?:number;color?:string;step?:number;winner?:number;odds?:number[];fighters?:ArenaFighter[];turn?:number;log?:string[];logs?:string[]};
export type TutorialState={discord_required:boolean;discord_verified:boolean;completed:boolean;reward_claimed:boolean;step:number;replay:boolean;gold:number;xp:number};
export type Snapshot = {save_owner?:string;objectives?:Objective[];daily_reward?:{gold:number;xp:number};economy_version?:string;campaign?:CampaignState;admin:boolean;tutorial:TutorialState;owned_story_items:{name:string;quantity:number}[];discord:null|{username:string;display_name:string;avatar_url:string};server_now:number;play:PlayState;tavern:{label:string;tier:number;remaining_today:number;cooldown_seconds:number;drinks_catalog:{key:string;name:string;available:boolean}[]};alley:{reputation:{label:string;tier:number;successes:number};access:{valid:boolean;seconds_left:number};fee:number;vip:boolean;invitations:number;larceny_remaining:number;ban_remaining:number;npc_targets:{key:string;name:string}[];heist:null|{attempts_left:number;code_length:number};record:Record<string,number>};arena:{champion?:ArenaChampion;recent?:ArenaResult[];remaining:number;champion_level:number;rating:number;champion_wins:number;skills:Record<string,{name:string;power?:number;accuracy?:number;emoji?:string}>};casino:{max_bet:number;horses:string[];odds:number[]};stats:Record<string,number|string>;quests:{key:string;label:string;target:number;progress:number;claimed:boolean}[];quest_reward:{gold:number;xp:number};podium:{name:string;total:number}[];chapters:{chapter:number;title:string;unlocked:boolean;can_unlock:boolean;missing:string[]}[];story_items:{name:string;chapter:number;price:number;owned:boolean}[];board:{batch_id:string;jobs:{job_id:string;title:string;rarity:string;reward:number}[]};pending:null|{ready:boolean;remaining:number;job:{title:string;reward:number}};name:string;level:number;xp:number;xp_needed:number;balance:{wallet:number;bank:number;free_withdrawal_available:boolean};owned:Record<string,boolean>;gear:Record<string,number>;resources:Record<string,number>;daily_available:boolean;active:null|{name:string;remaining:number;ends_at:number;started_at:number;capacity:number;revealed_loot:Record<string,number>;log:{drop_at:number;resource_name:string;quantity:number}[]};catalog:Record<string,{name:string;price:number}>;destinations:Record<string,{name:string;level:number;duration_label:string;duration_seconds?:number;tools:string[];location_key:string}>;tools:Record<string,Record<string,string>>;bags:Record<string,{name:string}>;recipes:Record<string,Record<string,number>>;bag_recipes:Record<string,Record<string,number>>;forge_levels:Record<string,number>;forge_gold:Record<string,Record<string,number>>;prices:Record<string,number>;objects:Record<string,{name:string}>};
const pendingKey='altherya.pending-operation.v1';
let pending:Record<string,unknown>|undefined;
try{const raw=localStorage.getItem(pendingKey);if(raw)pending=JSON.parse(raw);}catch{}
let mutating=false,owner:string|undefined;
function remember(value?:Record<string,unknown>){pending=value;try{if(value)localStorage.setItem(pendingKey,JSON.stringify(value));else localStorage.removeItem(pendingKey);}catch{}}
async function send(body?:Record<string,unknown>):Promise<{state:Snapshot;message:string}>{
 for(let attempt=0;attempt<2;attempt++){
  let r:Response;
  try{r=await fetch('/api/activity',body?{credentials:'include',method:'POST',headers:{'Content-Type':'application/json','X-Altherya-Request':'1'},body:JSON.stringify(body),signal:AbortSignal.timeout(20000)}:{credentials:'include',signal:AbortSignal.timeout(20000)});}catch(e){if(attempt===0)continue;throw new Error(body?'Connexion interrompue. Votre opération sera vérifiée à la reconnexion ; ne la relancez pas.':'Connexion au serveur interrompue.');}
  if(r.status>=500){if(attempt===0)continue;throw new Error('Serveur indisponible. Vérification de la sauvegarde en attente.');}
  const data=await r.json();
  if(!r.ok){if(body)remember();throw new Error(data.error??'Opération refusée');}
  owner=data.state?.save_owner;return data;
 }
 throw new Error('Serveur indisponible');
}
export async function request(body?:Record<string,unknown>):Promise<{state:Snapshot;message:string}>{
 if(mutating){if(body)throw new Error('Sauvegarde en cours. Patientez.');return send();}
 if(!body&&!pending)return send();
 mutating=true;
 try{
  if(pending){const old=pending;const result=await send(old);remember();if(!body||JSON.stringify(body)===JSON.stringify(Object.fromEntries(Object.entries(old).filter(([k])=>k!=='request_id'&&k!=='save_owner'))))return result;}
  if(!body)return send();
  const operation={...body,...(owner?{save_owner:owner}:{}),request_id:crypto.randomUUID()};remember(operation);
  const result=await send(operation);remember();return result;
 }finally{mutating=false;}
}
