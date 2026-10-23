# Correctif de compilation — 23 octobre 2026

## Cause confirmée

Le déploiement du commit fcc8a585bba6badc97f4cd81b38d816659a129ae échoue pendant `tsc --noEmit`, avant le démarrage du serveur. Les imports de `adventure-menu`, `ambience`, `asset-priority`, `combat-history`, `player-market` et `mailbox` ne trouvent pas leurs fichiers. L’import de `adventure-menu` est utilisé dans deux sources, ce qui explique les sept erreurs TS2307. L’erreur TS7006 sur `body` apparaît aussi dans ce code privé de ses types importés.

L’absence de `apps/game/src/ui/adventure-menu.ts` dans ce commit a été confirmée via GitHub. Le `.dockerignore` consulté n’exclut pas ces modules. L’archive cumulative précédente supposait une base Confort complète qui n’était pas intégralement présente dans le dépôt déployé.

## Contenu du correctif

Tout le code client, ses configurations et ses tests ; les modules et catalogues API ; les moteurs Python du bot utilisés par l’API ; les sources et assets cumulatifs Popie/Panda/Smogo. Les nouveaux fichiers sont livrés avec leurs dépendances, au lieu de limiter l’archive aux seuls fichiers modifiés.

Les autres assets du projet existant doivent être conservés. Aucun fichier de données, environnement, dépendance installée ou build généré n’est livré. Aucun changement de port, de secret Discord, de récompense ou de tarif n’est nécessaire pour résoudre cette erreur.

## Validation locale

- Build TypeScript/Vite du code réuni : réussi, sans TS2307 ni TS7006.
- Vérification supplémentaire depuis le ZIP extrait dans un dossier initialement vide : installation des dépendances, build TypeScript/Vite, import de l’API, chargement des catalogues et snapshot des modules PNJ réussis. Aucun ancien fichier de code n’était disponible dans ce dossier de contrôle. Les assets du jeu existant restent à conserver lors de l’installation réelle.
- 18 tests ciblés réussis : journal (ouverture, pagination, détails) et menus des trois PNJ.
- Compilation des modules Python API et bot : réussie.
- Initialisation de l’API, chargement des catalogues, construction d’un snapshot et présence des trois modules PNJ : réussis sur une base temporaire.

Les audits précédents sont conservés comme historique, sans prétendre que leurs suites entières ont été rejouées pour ce correctif de conditionnement. Le préchargement intermittent observé précédemment reste un point distinct de l’échec de compilation montré dans ce log.

Aucune modification du dépôt distant, de Coolify ou des données de production n’a été effectuée.
