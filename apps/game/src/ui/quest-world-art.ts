/** Individually generated transparent props. IDs are whitelisted, never supplied as URLs. */
export const questWorldAssets={recu:'recu.png',attestation:'attestation.png',plaque:'plaque.png',journal:'journal.png',balise:'balise.png',etais:'etais.png'} as const;
export type QuestWorldAsset=keyof typeof questWorldAssets;
export function questWorldArt(id:string){
 if(!Object.hasOwn(questWorldAssets,id))return undefined;
 const key=id as QuestWorldAsset,image=document.createElement('img');image.src='/assets/quest-world/v1/'+questWorldAssets[key];image.alt='';image.decoding='async';image.draggable=false;image.className='world-prop-art';image.dataset.questAsset=key;return image;
}
const terrain:Record<string,Record<string,QuestWorldAsset>>={
 'S2-Q07-O2':{'1':'etais'},
 'S3-Q03-O1':{'0':'balise'},'S3-Q03-O2':{'0':'balise'},
 'S4-Q07-O2':{'1':'balise'},
};
export function terrainQuestAsset(stepId:string,pointId:string){const points=Object.hasOwn(terrain,stepId)?terrain[stepId]:undefined;return points&&Object.hasOwn(points,pointId)?points[pointId]:undefined;}
