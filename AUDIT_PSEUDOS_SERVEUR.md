# Audit — surnoms du serveur

## Implémentation

- Nouveau module guild_names.py : association du serveur au salon portail obtenue par l’API Discord avec le token bot ; récupération ciblée du membre vérifié par son ID OAuth ; priorité surnom serveur → global_name → username.
- Cache SQLite du nom de compte, du surnom et du serveur. Aucun ALTER des tables de solde ni nouvelle identité joueur. Mise à jour atomique du nom d’affichage dans le profil, toutes ses sessions et les reçus du tutoriel.
- Actualisation à chaque connexion, révision progressive des comptes canoniques existants en arrière-plan. Pas de liste de tous les membres du serveur. Pas de nouveau scope OAuth ou intent privilégié.
- Noms visibles des combattants actifs alignés sur le profil courant ; prochaines Gazettes lisant le nom actuel plutôt qu’un ancien nom enregistré au moment du résultat.
- Échecs réseau/403 conservant le cache du même serveur, absence de surnom/membre rétablissant le nom de compte, 429 et 401/403 avec pauses de protection. Aucun nom, serveur ou rôle envoyé par le navigateur n’est utilisé pour décider de l’identité ou des droits.

## Vérifications locales

- Compilation de tous les modules API et moteurs Python du bot : réussie. Revue des nouveaux imports et du code modifié.
- **156 tests API réussis**, dont **26 tests de surnoms** : priorité des noms, retrait de surnom, repli global/username, réseau/403/404/429, membre incohérent rejeté, surnom invalide, serveur obtenu par le salon, cache du serveur, cadence, nouvelle connexion/cache, redémarrage, toutes sessions/reçu, changement de serveur, rattrapage limité aux comptes connus, absence de droits admin par usurpation de nom, absence de token, nom de combattant et Gazette, anciens doublons de profils ignorés dans les noms Gazette/logs admin au profit du compte canonique, OAuth réel côté API avec transport simulé ignorant le pseudo/serveur soumis par le navigateur, connexion continuant en cas de refus du bot.
- Build TypeScript/Vite : réussi. **47 tests frontend réussis**. Aucun changement de code ou CSS frontend fonctionnel.
- **15 contrôles navigateur spécifiques**, sans erreur JS, sur PC 1440×900, fenêtre courte 1186×570 et mobile 390×844 : surnom long avec symboles dans le HUD/profil, nom correct dans la recherche et la fiche admin, menus contenus dans le viewport. Inspection visuelle du profil mobile réalisée. Avatars non testés dans cette passe : requêtes d’images neutralisées dans le test navigateur, aucun changement du code des avatars.
- Comparaison à la version Menu Portail V2 : assets et moteurs originaux du bot inchangés. Changements limités à activity.py, server.py, play.py, discord_events.py, nouveau module de noms, tests et documentation.
- Archives ZIP : CRC vérifié, fichier règles source et image du portail conservés. Reconstruction TypeScript/Vite depuis l’archive complète extraite réussie.

## Limites restantes

Pas d’accès authentifié au serveur Coolify ou au bot réel dans cet environnement. Les réponses Discord/membres des tests sont simulées ; aucun surnom privé du serveur réel n’a été téléchargé ici, aucun message Discord n’a été envoyé et aucun nom de membre n’a été modifié sur Discord. Après déploiement, vérifier avec un joueur dont le surnom serveur diffère du nom global.

La synchronisation n’est pas instantanée pendant une session : cadence de rattrapage limitée, vérification périodique après cinq minutes minimum et actualisation du client à son rythme existant. Une reconnexion demande immédiatement une nouvelle lecture. Les messages déjà publiés et les textes de combat historiques ne sont pas réécrits. Les identifiants, autorisations et récompenses ne dépendent jamais des noms.

Les mêmes tests de régression continuent de valider les règles de solde et de tutoriel locales, mais aucune validation de Gold partagé Oddium/PostgreSQL en production n’a été faite. Cette architecture reste inchangée. Aucun reset des données ni changement de port.

## Documentation primaire

https://docs.discord.com/developers/resources/guild — Get Guild Member, Guild Member Structure.
https://docs.discord.com/developers/resources/user — User Structure et portée identify existante.
