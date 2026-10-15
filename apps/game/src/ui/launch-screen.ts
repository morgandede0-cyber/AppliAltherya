/** Progress represents completed startup tasks, never an elapsed-time estimate. */
export function launchScreen(retry:()=>void){
 const root=document.createElement('section');root.id='launch-screen';root.setAttribute('aria-label','Lancement d’Althérya');
 const content=document.createElement('div');content.className='launch-content';
 const logo=document.createElement('img');logo.className='launch-logo';logo.src='/assets/launch/royal-crest.png';logo.alt='Althérya';logo.fetchPriority='high';
 const meter=document.createElement('div');meter.className='launch-meter';meter.setAttribute('role','progressbar');meter.setAttribute('aria-label','Progression du lancement');meter.setAttribute('aria-valuemin','0');meter.setAttribute('aria-valuemax','100');
 const fill=document.createElement('div');fill.className='launch-fill';const value=document.createElement('span');value.className='launch-value';meter.append(fill,value);
 const message=document.createElement('p');message.className='launch-message';message.setAttribute('role','status');message.setAttribute('aria-live','polite');
 const steps=document.createElement('ol');steps.className='launch-steps';
 const items=['Discord','Personnage','Monde'].map((label,i)=>{const li=document.createElement('li'),icon=document.createElement('span'),text=document.createElement('span');icon.className='launch-step-icon';const symbols=['<path d="M7 6 4 7C2 11 2 15 3 18l4 2 1-2m9-12 3 1c2 4 2 8 1 11l-4 2-1-2M7 6c3-1 7-1 10 0M7 17c3 2 7 2 10 0"/><circle cx="8.5" cy="12" r="1"/><circle cx="15.5" cy="12" r="1"/>','<circle cx="12" cy="7" r="4"/><path d="M4 22v-3a8 8 0 0 1 16 0v3Z"/>','<circle cx="12" cy="12" r="10"/><ellipse cx="12" cy="12" rx="4" ry="10"/><path d="M2 12h20M4 6h16M4 18h16"/>'];icon.innerHTML='<svg viewBox="0 0 24 24" focusable="false">'+symbols[i]+'</svg>';icon.setAttribute('aria-hidden','true');text.textContent=label;li.append(icon,text);steps.append(li);return li;});
 const again=document.createElement('button');again.type='button';again.className='launch-retry';again.textContent='Réessayer';again.hidden=true;again.onclick=retry;
 content.append(logo,meter,message,steps,again);root.append(content);document.body.append(root);document.body.classList.add('launching');
 let progress=0;
 function update(next:number,label:string,step:number){progress=Math.max(progress,Math.min(100,Math.round(next)));meter.setAttribute('aria-valuenow',String(progress));meter.setAttribute('aria-valuetext',`${progress} % · ${label}`);fill.style.width=progress+'%';value.textContent=progress+' %';message.textContent=label;items.forEach((li,i)=>{li.dataset.status=i<step?'done':i===step?'active':'waiting';if(i===step)li.setAttribute('aria-current','step');else li.removeAttribute('aria-current');});}
 update(0,'Préparation de votre aventure…',0);
 return {update,local(){items[0].lastElementChild!.textContent='Session';},error(text:string){root.classList.add('launch-error');message.textContent=text;message.setAttribute('role','alert');again.hidden=false;again.focus();},destroy(){root.remove();document.body.classList.remove('launching');}};
}

export async function preloadLaunchAssets(urls:string[],onProgress:(done:number,total:number)=>void){
 let done=0,failed=false;await Promise.all(urls.map(src=>new Promise<void>((resolve,reject)=>{
  const image=new Image(),timeout=window.setTimeout(()=>{failed=true;reject(new Error('Chargement trop long. Vérifiez votre connexion puis réessayez.'));},15000);
  image.onload=()=>{clearTimeout(timeout);done++;if(!failed)onProgress(done,urls.length);resolve();};
  image.onerror=()=>{failed=true;clearTimeout(timeout);reject(new Error('Un élément du décor ne peut pas être chargé. Réessayez dans quelques instants.'));};image.src=src;
 })));
}
