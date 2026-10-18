import {fitNineSlices} from './nine-slice';
/** Refit native labels and keep an open menu inside the visible viewport. */
export function watchFrameContainment(panel:HTMLElement){
 let frame=0,dead=false;
 const fonts=new WeakMap<HTMLElement,{value:string;priority:string}>();
 function fit(){
  if(dead||panel.hidden||!panel.isConnected)return;
  const view=window.visualViewport,w=view?.width??innerWidth,h=view?.height??innerHeight,ox=view?.offsetLeft??0,oy=view?.offsetTop??0;
  panel.style.setProperty('--frame-viewport-height',h+'px');
  panel.style.setProperty('translate','0px 0px','important');
  const r=panel.getBoundingClientRect();
  const dx=r.left<ox+8?ox+8-r.left:r.right>ox+w-8?ox+w-8-r.right:0;
  const dy=r.top<oy+8?oy+8-r.top:r.bottom>oy+h-8?oy+h-8-r.bottom:0;
  if(dx||dy)panel.style.setProperty('translate',`${dx}px ${dy}px`,'important');
  fitNineSlices(panel);
  for(const label of Array.from(panel.querySelectorAll<HTMLElement>('.predator-button-content,.approved-button-content,.gm-button-label'))){
   const button=label.closest('button');if(!button||!button.getClientRects().length||button.clientWidth===0)continue;
   if(!fonts.has(label))fonts.set(label,{value:label.style.getPropertyValue('font-size'),priority:label.style.getPropertyPriority('font-size')});
   const original=fonts.get(label)!;if(original.value)label.style.setProperty('font-size',original.value,original.priority);else label.style.removeProperty('font-size');
   const style=getComputedStyle(button),availableW=button.clientWidth-parseFloat(style.paddingLeft)-parseFloat(style.paddingRight),availableH=button.clientHeight-parseFloat(style.paddingTop)-parseFloat(style.paddingBottom);
   if(availableW<=0||availableH<=0)continue;
   let size=parseFloat(getComputedStyle(label).fontSize);
   while(size>11&&(label.scrollWidth>availableW+1||label.scrollHeight>availableH+1)){size-=.5;label.style.setProperty('font-size',size+'px','important');}
  }
 }
 function schedule(){if(dead)return;cancelAnimationFrame(frame);frame=requestAnimationFrame(fit);}
 const observer=new MutationObserver(schedule);observer.observe(panel,{childList:true,subtree:true,attributes:true,attributeFilter:['class','hidden','data-kind','aria-busy']});
 const geometry=new ResizeObserver(schedule);geometry.observe(panel);
 window.addEventListener('resize',schedule);window.visualViewport?.addEventListener('resize',schedule);window.visualViewport?.addEventListener('scroll',schedule);
 document.fonts?.ready.then(schedule);schedule();
 return()=>{dead=true;cancelAnimationFrame(frame);observer.disconnect();geometry.disconnect();window.removeEventListener('resize',schedule);window.visualViewport?.removeEventListener('resize',schedule);window.visualViewport?.removeEventListener('scroll',schedule);panel.style.removeProperty('translate');panel.style.removeProperty('--frame-viewport-height');};
}
