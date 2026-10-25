import fs from 'node:fs';
import path from 'node:path';
const root=path.resolve(import.meta.dirname,'..'),missing=new Map();let references=0;
function walk(dir){return fs.readdirSync(dir,{withFileTypes:true}).flatMap(e=>e.isDirectory()?walk(path.join(dir,e.name)):[path.join(dir,e.name)]);}
for(const file of walk(path.join(root,'src'))){if(!/\.(ts|css|json)$/.test(file))continue;for(const match of fs.readFileSync(file,'utf8').matchAll(/["'(](\/assets\/[^"'`\s)<>]+)/g)){const asset=match[1].split('?')[0];if(/[+$*]/.test(asset)||!path.extname(asset))continue;references++;if(!fs.existsSync(path.join(root,'public',asset)))missing.set(asset,path.relative(root,file));}}
console.log(JSON.stringify({references,missing:[...missing].map(([asset,source])=>({asset,source}))},null,2));if(missing.size)process.exitCode=1;
