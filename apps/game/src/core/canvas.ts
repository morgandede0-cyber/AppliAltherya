/** Canvas compatibility renderer: same scene primitives as the Pixi client,
 * drawing the actual PNG assets, without WebGL/WebGPU or GPU requirements. */
class Point {
 constructor(public x=0,public y=0){}
 set(x:number,y=x){this.x=x;this.y=y;}
}
export class Rectangle {constructor(public x:number,public y:number,public width:number,public height:number){}}
export class Texture {
 source:HTMLImageElement;frame:Rectangle;
 constructor(options:{source:HTMLImageElement;frame?:Rectangle}){this.source=options.source;this.frame=options.frame??new Rectangle(0,0,this.source.naturalWidth,this.source.naturalHeight);}
 get width(){return this.frame.width;}get height(){return this.frame.height;}
}
const cache=new Map<string,Promise<Texture>>();
export const Assets={load(url:string):Promise<Texture>{let result=cache.get(url);if(!result){result=new Promise((resolve,reject)=>{const img=new Image();const timer=setTimeout(()=>reject(new Error(`Chargement trop long : ${url}`)),15000);img.onload=()=>{clearTimeout(timer);resolve(new Texture({source:img}));};img.onerror=()=>{clearTimeout(timer);reject(new Error(`Image inaccessible : ${url}`));};img.src=url;});cache.set(url,result);}return result;}};
export class Container {
 position=new Point();scale=new Point(1,1);visible=true;children:Container[]=[];
 get x(){return this.position.x;}set x(v:number){this.position.x=v;}get y(){return this.position.y;}set y(v:number){this.position.y=v;}
 addChild<T extends Container>(child:T){this.children.push(child);return child;}
 render(ctx:CanvasRenderingContext2D){if(!this.visible)return;ctx.save();ctx.translate(this.x,this.y);ctx.scale(this.scale.x,this.scale.y);this.draw(ctx);for(const child of this.children)child.render(ctx);ctx.restore();}
 protected draw(_ctx:CanvasRenderingContext2D){}
}
export class Sprite extends Container {
 anchor=new Point();constructor(public texture:Texture){super();}
 get width(){return this.texture.width*Math.abs(this.scale.x);}set width(value:number){this.scale.x=value/this.texture.width;}
 get height(){return this.texture.height*Math.abs(this.scale.y);}set height(value:number){this.scale.y=value/this.texture.height;}
 protected draw(ctx:CanvasRenderingContext2D){const f=this.texture.frame;ctx.drawImage(this.texture.source,f.x,f.y,f.width,f.height,-this.anchor.x*f.width,-this.anchor.y*f.height,f.width,f.height);}
}
export class Text extends Container {
 anchor=new Point();text:string;style:{fontFamily?:string;fontSize?:number;fill?:number;stroke?:{color:number;width:number}};
 constructor(o:{text:string;style:Text['style']}){super();this.text=o.text;this.style=o.style;}
 protected draw(ctx:CanvasRenderingContext2D){ctx.font=`${this.style.fontSize??14}px ${this.style.fontFamily??'Georgia'}`;ctx.textBaseline='top';const width=ctx.measureText(this.text).width,x=-this.anchor.x*width,y=-this.anchor.y*(this.style.fontSize??14);if(this.style.stroke){ctx.strokeStyle=color(this.style.stroke.color);ctx.lineWidth=this.style.stroke.width;ctx.lineJoin='round';ctx.strokeText(this.text,x,y);}ctx.fillStyle=color(this.style.fill??0xffffff);ctx.fillText(this.text,x,y);}
}
function color(value:number){return '#'+value.toString(16).padStart(6,'0');}
export class Application {
 canvas=document.createElement('canvas');stage=new Container();screen={width:1,height:1};
 ticker={add:(fn:(tick:{deltaMS:number})=>void)=>{this.callbacks.push(fn);}};
 private callbacks:((tick:{deltaMS:number})=>void)[]=[];
 async init(options:{resizeTo:HTMLElement;background:number;antialias:boolean;resolution:number;autoDensity:boolean}){
  const ctx=this.canvas.getContext('2d',{alpha:false});if(!ctx)throw new Error('Le navigateur ne permet pas le rendu Canvas 2D.');
  const resize=()=>{const w=Math.max(1,options.resizeTo.clientWidth),h=Math.max(1,options.resizeTo.clientHeight);this.screen={width:w,height:h};this.canvas.width=Math.round(w*options.resolution);this.canvas.height=Math.round(h*options.resolution);this.canvas.style.width=w+'px';this.canvas.style.height=h+'px';};resize();new ResizeObserver(resize).observe(options.resizeTo);
  let previous=performance.now();const frame=(now:number)=>{const deltaMS=Math.min(now-previous,50);previous=now;for(const fn of this.callbacks)fn({deltaMS});ctx.setTransform(options.resolution,0,0,options.resolution,0,0);ctx.imageSmoothingEnabled=options.antialias;ctx.fillStyle=color(options.background);ctx.fillRect(0,0,this.screen.width,this.screen.height);this.stage.render(ctx);requestAnimationFrame(frame);};requestAnimationFrame(frame);
 }
}
