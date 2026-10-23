/** In-memory, account-scoped presentation only; never stores rewards or balances. */
const preferences=new Map<string,unknown>();
export function recall<T>(owner:string|undefined,scope:string,fallback:T):T{return owner?(preferences.get(owner+':'+scope) as T??fallback):fallback;}
export function remember<T>(owner:string|undefined,scope:string,value:T){if(!owner)return;if(preferences.size>128)preferences.delete(preferences.keys().next().value!);preferences.set(owner+':'+scope,structuredClone(value));}
