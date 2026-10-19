/** Owns the visible UI layer, including nested confirmations and background controls. */
export function watchMenuSurface(panel:HTMLElement,scene:HTMLElement){
 const suspended=new Map<HTMLElement,{inert:boolean;ariaHidden:string|null}>();
 function restore(){for(const [node,old] of suspended){node.removeAttribute('data-menu-suspended');if(node.inert)node.inert=old.inert;if(old.ariaHidden===null)node.removeAttribute('aria-hidden');else node.setAttribute('aria-hidden',old.ariaHidden);}suspended.clear();}
 function suspend(node:HTMLElement){if(suspended.has(node))return;suspended.set(node,{inert:node.inert,ariaHidden:node.getAttribute('aria-hidden')});node.dataset.menuSuspended='';node.inert=true;node.setAttribute('aria-hidden','true');}
 function sync(){
  restore();const open=!panel.hidden;document.body.classList.toggle('menu-open',open);scene.inert=open||scene.getAttribute('aria-busy')==='true';if(open)scene.setAttribute('aria-hidden','true');else scene.removeAttribute('aria-hidden');
  const overlay=open?panel.querySelector<HTMLElement>('.merchant-modal,.art-extra,.game-help-overlay'):null;
  panel.toggleAttribute('data-modal-open',!!overlay);panel.setAttribute('role',overlay?'presentation':'dialog');if(overlay)panel.removeAttribute('aria-modal');else panel.setAttribute('aria-modal','true');
  if(overlay){let branch:HTMLElement=overlay;while(branch!==panel&&branch.parentElement){const parent=branch.parentElement;for(const sibling of Array.from(parent.children))if(sibling!==branch&&sibling instanceof HTMLElement)suspend(sibling);branch=parent;}}
 }
 const observer=new MutationObserver(sync);observer.observe(panel,{childList:true,subtree:true,attributes:true,attributeFilter:['hidden']});observer.observe(scene,{attributes:true,attributeFilter:['aria-busy']});sync();
 return()=>{observer.disconnect();restore();document.body.classList.remove('menu-open');scene.inert=false;scene.removeAttribute('aria-hidden');panel.removeAttribute('data-modal-open');};
}
