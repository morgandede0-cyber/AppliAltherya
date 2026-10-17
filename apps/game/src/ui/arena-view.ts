import type {Snapshot} from '../activity';
import {assetSlice} from './assets';
import {node,menuStat} from './menu-framework';
export function championRank(level:number){return ['I','II','III','IV','V','VI','VII','VIII','IX','X'][level-1]??String(level);}
/** Every value is supplied by the current server snapshot. */
export function arenaSummary(s:Snapshot){
 const section=node('section','arena-summary');
 const emblem=node('div','arena-emblem');emblem.append(assetSlice('/assets/menus/arena.webp',45,205,715,480));section.append(emblem);
 const info=node('div','arena-summary-copy');info.append(node('p','arena-kicker','DÉFI DU CHAMPION'),node('h3','arena-champion-title','Champion '+championRank(s.arena.champion_level)));
 const champion=s.arena.champion;if(champion){info.append(node('p','arena-champion-name',champion.name),node('p','arena-champion-role',champion.role),node('p','arena-champion-hint',champion.hint));section.style.setProperty('--champion-accent',champion.color);}
 const stats=node('div','arena-summary-stats');menuStat(stats,'Classement',String(s.arena.rating));menuStat(stats,'Champions vaincus',String(s.arena.champion_wins));menuStat(stats,'Portefeuille',`${s.balance.wallet} Gold`);
 const active=s.play.kind==='combat'&&s.play.status==='active';
 const availability=node('p','arena-availability',active?'Un combat vous attend.':s.arena.remaining>0?'Le champion se prépare pour votre prochain défi.':'Le champion est prêt à vous affronter.');
 if(s.arena.remaining>0&&!active){const clock=node('span','arena-cooldown');clock.dataset.deadline=String(Date.now()+s.arena.remaining*1000);clock.textContent=String(s.arena.remaining)+' s';availability.append(clock);}
 section.append(info,stats,availability);
 if(s.arena.recent?.length){const history=node('section','arena-recent');history.append(node('h4','','Dernières rencontres'));for(const r of s.arena.recent.slice(0,3))history.append(node('p','',`${r.won?'Victoire':'Défaite'} · ${r.champion.name} · ${r.net_gold>0?'+':''}${r.net_gold} Gold · +${r.xp} XP`));section.append(history);}return section;
}
