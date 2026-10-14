/** Detection affects initialization only; identity/permissions stay on the server. */
export function isDiscordActivity(url:Pick<Location,'search'|'hostname'>=location){return new URLSearchParams(url.search).has('frame_id')||/^\d+\.discordsays\.com$/.test(url.hostname);}
export function connectionError(error:unknown){
 if(error instanceof Error)return error.message;
 if(error&&typeof error==='object'){
  const e=error as {message?:unknown;code?:unknown;error?:unknown};
  const message=typeof e.message==='string'?e.message:typeof e.error==='string'?e.error:'Autorisation Discord refusée';
  return message+(typeof e.code==='number'||typeof e.code==='string'?` (code ${e.code})`:'');
 }
 return typeof error==='string'?error:'Connexion Discord indisponible. Fermez puis relancez l’activité.';
}
