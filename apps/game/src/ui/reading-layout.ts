/** Bound illustrated readers to the current visual viewport and visible HUD. */
export function fitReadingPanel(panel:HTMLElement,kind:'book'|'guide'){
 const view=panel.ownerDocument.defaultView;if(!view)return;const v=view.visualViewport,top=v?.offsetTop??0,height=v?.height??view.innerHeight,width=v?.width??view.innerWidth;
 const hud=panel.ownerDocument.getElementById('hud'),bottom=hud&&!hud.hidden?hud.getBoundingClientRect().bottom:top;
 const inset=Math.max(top+8,Math.min(bottom+8,top+height*.23));
 panel.style.setProperty(kind==='guide'?'--guide-top':'--book-top',inset+'px');
 panel.style.setProperty('--reading-height',Math.max(100,top+height-inset-12)+'px');
 panel.style.setProperty('--reading-width',Math.max(100,width-16)+'px');
}
