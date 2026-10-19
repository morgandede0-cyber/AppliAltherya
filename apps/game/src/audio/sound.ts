let context:AudioContext|undefined;export let enabled=false;
export function toggle(){enabled=!enabled;if(enabled){context??=new AudioContext();void context.resume();}return enabled;}
export function chime(high=false){if(!enabled||!context)return;const now=context.currentTime;[0,1,2].forEach((n)=>{const o=context!.createOscillator(),g=context!.createGain();o.type='triangle';o.frequency.value=(high?440:220)*[1,1.25,1.5][n];g.gain.setValueAtTime(.04,now+n*.08);g.gain.exponentialRampToValueAtTime(.001,now+n*.08+.25);o.connect(g).connect(context!.destination);o.start(now+n*.08);o.stop(now+n*.08+.26);});}

/** Short synthetic leather/wood contact, respecting the game's existing audio toggle. */
export function diceTap(strength=.5){if(!enabled||!context)return;const now=context.currentTime,buffer=context.createBuffer(1,Math.floor(context.sampleRate*.045),context.sampleRate),data=buffer.getChannelData(0);for(let i=0;i<data.length;i++)data[i]=(Math.random()*2-1)*(1-i/data.length)**3;const source=context.createBufferSource(),filter=context.createBiquadFilter(),gain=context.createGain();source.buffer=buffer;filter.type='lowpass';filter.frequency.value=1800;gain.gain.value=.035*Math.max(0,Math.min(1,strength));source.connect(filter).connect(gain).connect(context.destination);source.start(now);source.stop(now+.05);}

/** Short synthetic brass contact; respects the existing opt-in audio toggle. */
export function coinTap(strength=.5){
 if(!enabled||!context)return;
 const now=context.currentTime,volume=Math.max(0,Math.min(1,strength));
 diceTap(volume*.35);
 for(const [i,hz] of [2350,3860,5940].entries()){
  const oscillator=context.createOscillator(),gain=context.createGain();
  oscillator.type='sine';oscillator.frequency.value=hz;
  gain.gain.setValueAtTime(.025*volume/(i+1),now);
  gain.gain.exponentialRampToValueAtTime(.0001,now+.15);
  oscillator.connect(gain).connect(context.destination);oscillator.start(now);oscillator.stop(now+.16);
 }
}
