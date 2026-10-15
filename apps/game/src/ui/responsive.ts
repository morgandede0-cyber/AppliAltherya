export type SceneViewport={width:number;height:number;portrait:boolean};
/** Choose layout by usable Activity viewport, including narrow desktop windows. */
export function sceneViewport(width:number,height:number,ratio:number):SceneViewport{
 const portrait=width/height<1.15;
 if(portrait)return {width,height,portrait};
 const available=Math.max(1,height-(height<500?48:68));
 const fitted=Math.min(width,available*ratio);
 return {width:fitted,height:fitted/ratio,portrait};
}
