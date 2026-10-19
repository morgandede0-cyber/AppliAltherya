export const FACE_VALUES=[1,6,3,4,2,5];
export const NORMALS=[[0,0,1],[0,0,-1],[1,0,0],[-1,0,0],[0,-1,0],[0,1,0]];
export const PIPS:Record<number,number[][]>={1:[[1,1]],2:[[0,0],[2,2]],3:[[0,0],[1,1],[2,2]],4:[[0,0],[2,0],[0,2],[2,2]],5:[[0,0],[2,0],[1,1],[0,2],[2,2]],6:[[0,0],[2,0],[0,1],[2,1],[0,2],[2,2]]};
export function faceToTop(value:number){return({1:{x:90,z:0},2:{x:0,z:0},3:{x:0,z:-90},4:{x:0,z:90},5:{x:180,z:0},6:{x:-90,z:0}} as Record<number,{x:number;z:number}>)[value]??{x:90,z:0};}
export function rotateX(v:number[],a:number){const c=Math.cos(a*Math.PI/180),s=Math.sin(a*Math.PI/180);return[v[0],v[1]*c-v[2]*s,v[1]*s+v[2]*c];}
export function rotateZ(v:number[],a:number){const c=Math.cos(a*Math.PI/180),s=Math.sin(a*Math.PI/180);return[v[0]*c-v[1]*s,v[0]*s+v[1]*c,v[2]];}
export function diceMotion(seconds:number,side:number){const duration=2.6+side*.45,t=Math.min(1,Math.max(0,(seconds-side*.12)/duration)),ease=1-(1-t)**3,tail=1-ease;return{t,contacts:Math.min(3,Math.floor(3*t**.65)),x:(side?.64:.36)+(side?.08:-.09)*tail+.035*Math.sin(t*Math.PI)*Math.sin(t*Math.PI*2+side),y:.52-.13*tail,z:82*Math.abs(Math.sin(Math.PI*3*t**.65))*(1-t)**1.6,rx:t===1?0:1080*tail,rz:t===1?0:(side?-720:720)*tail,stopped:t>=1};}
export function dieTransform(value:number,rx=0,rz=0,side=0){const p=faceToTop(value);return`rotateX(${-55+rx}deg) rotateZ(${(side?-12:12)+rz}deg) rotateX(${p.x}deg) rotateZ(${p.z}deg)`;}
export function faceShade(normal:number[],value:number,rx:number,rz:number,side:number){const p=faceToTop(value),n=rotateX(rotateZ(rotateX(rotateZ(normal,p.z),p.x),(side?-12:12)+rz),-55+rx);return .38*(1-Math.max(0,n[0]*-.3+n[1]*-.5+n[2]*.8));}
