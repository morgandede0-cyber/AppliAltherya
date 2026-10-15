export type SceneViewport={width:number;height:number;portrait:boolean};
/** Keep the original authored scene and button coordinates in every viewport. */
export function sceneViewport(width:number,height:number,ratio:number):SceneViewport{
 const fitted=Math.min(width,height*ratio);
 return {width:fitted,height:fitted/ratio,portrait:width/height<1.15};
}
