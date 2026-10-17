/** Newest first. Use actual release dates; only completed changes belong here. */
export type UpdateNote={id:string;date:string;category:string;title:string;summary:string;changes:string[]};
export const updateNotes:UpdateNote[]=[
 {id:'annonces-20261017',date:'2026-10-17',category:'Nouveauté',title:'Petites annonces',summary:'Plus de choix, une surprise à la signature.',changes:['8 annonces aléatoires au choix, réparties sur deux pages.','Le rang et la récompense se révèlent à la signature du contrat.','Les contrats déjà signés conservent leur récompense et leur durée.']},
 {id:'techniques-20261017',date:'2026-10-17',category:'Combat',title:'Les techniques des champions',summary:'Apprenez de vos victoires et composez votre arsenal.',changes:['Une technique se débloque en battant son champion.','Remplacez librement vos techniques entre les combats.','Chaque technique possède ses avantages et ses limites.']},
 {id:'arene-20261017',date:'2026-10-17',category:'Combat',title:'Une arène plus vivante',summary:'Des adversaires aux tactiques différentes.',changes:['Les champions disposent de comportements de combat distincts.','Le duel affiche les intentions, les effets et le journal des attaques.','Un écran de résultat détaille les gains et le déroulement du combat.']}
];
