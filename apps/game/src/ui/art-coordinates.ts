/** Coordinates measured in original artwork pixels. One definition for PC and mobile. */
export type ArtRect=readonly [number,number,number,number];
export const menuGeometry={
 tavern:{size:[1984,793],actions:[[40,388,655,175],[695,388,595,175],[1290,388,655,175],[705,565,585,140]]},
 alley:{size:[2172,724],actions:[[22,340,520,126],[562,340,500,126],[1086,340,500,126],[1608,340,540,126],[825,510,525,130]]},
 thief:{size:[2172,724],actions:[[22,326,520,140],[562,326,500,140],[1086,326,500,140],[1608,326,540,140],[825,522,525,130]]},
 castle:{size:[1536,1024],actions:[[34,350,502,443],[536,350,467,443],[1004,350,496,443],[475,812,584,115]]},
 arena:{size:[1536,1024],actions:[[24,202,737,669],[786,200,731,670],[450,881,635,120]]},
 expedition:{size:[1536,1024],actions:[[35,240,482,540],[520,240,490,540],[1010,240,485,540],[538,800,460,72],[538,900,470,90]]},
 games:{size:[1536,1024],actions:[[60,266,462,287],[538,266,462,287],[1014,266,462,287],[490,922,568,72]]},
 casino:{size:[1536,1024],actions:[[16,287,476,184],[522,287,476,184],[1030,287,490,184],[16,583,476,184],[522,583,476,184],[1030,583,490,184]]},
} satisfies Record<string,{size:number[];actions:number[][]}>;
export function percentages(rect:ArtRect,width=1536,height=1024):[number,number,number,number]{return [rect[0]/width*100,rect[1]/height*100,rect[2]/width*100,rect[3]/height*100];}
export function navigationRect(kind:string,index:number){const g=menuGeometry[kind as keyof typeof menuGeometry];if(!g?.actions[index])throw new Error(`Zone graphique absente : ${kind}/${index}`);return percentages(g.actions[index] as [number,number,number,number],g.size[0],g.size[1]);}
