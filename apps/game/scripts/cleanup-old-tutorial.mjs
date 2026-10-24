// Retire only the superseded tutorial artwork, including files left by an overlay update.
import {unlink} from 'node:fs/promises';
const retired=[...Array.from({length:6},(_,i)=>`page-${i}.png`),'guide-skin-v2.png'];
for(const name of retired){try{await unlink(new URL('../public/assets/tutorial/'+name,import.meta.url));}catch(error){if(error.code!=='ENOENT')throw error;}}
