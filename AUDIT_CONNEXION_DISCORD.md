# Correctif de session Discord Activity

## Défaut identifié
La version 22 utilise SameSite=Strict pour la session Activity. Dans une iframe hébergée par Discord, ce cookie peut être bloqué ; après l’autorisation OAuth, le prochain chargement ne retrouve alors aucun profil vérifié et affiche « Connexion Discord requise ». L’erreur JavaScript précédente affichée comme [objet Object] ne permettait pas non plus d’identifier l’étape en échec.

Référence officielle : https://docs.discord.com/developers/activities/development-guides/networking#using-cookies . Discord demande SameSite=None et Partitioned pour ses iframes.

## Corrections
- Helper commun activity_cookie.py, utilisé par l’API Activity et la passerelle OAuth. En configuration Discord sur l’hébergement, le cookie devient HttpOnly ; Secure ; SameSite=None ; Partitioned ; Path=/. Il est limité à l’hôte de la réponse, donc au domaine application_id.discordsays.com lorsque la réponse passe par le proxy. Aucun Domain=magicgg.fr incompatible avec le proxy n’est imposé.
- Secure est conservé même si la connexion entre le reverse proxy et Python est en HTTP. Le test direct HTTP sur localhost reste possible. Les sessions déjà connues sont réémises avec les nouveaux attributs ; aucune base ni progression n’est effacée.
- Compatibilité Python 3.12 : Partitioned est sérialisé dans Set-Cookie, sans exiger sa prise en charge par http.cookies.Morsel.
- Les appels frontend de connexion et de jeu incluent explicitement les credentials.
- Le POST OAuth demande lui aussi l’en-tête anti-CSRF X-Altherya-Request: 1 ; les anciennes protections du jeu et de l’admin sont conservées.
- Détection de l’Activity par frame_id ou par le domaine numérique exact de son proxy Discord. Cette détection n’accorde aucune identité ni permission : celles-ci proviennent toujours du serveur OAuth.
- Messages d’erreur contenant l’étape, le message et le code SDK quand disponibles, sans sérialiser les tokens ni l’ensemble des données. Délai limite pour les commandes RPC et la connexion ; une seule connexion SDK par page et verrouillage des relances simultanées.
- Si OAuth réussit mais que le profil ne revient pas dans le snapshot, l’écran signale précisément la session non conservée. Le HTML de démarrage est servi sans cache pour éviter le mélange de versions.

## Vérifications effectuées
Compilation TypeScript/Vite et Python API ; 47 tests frontend ; 69 tests API, dont les nouveaux tests des attributs, hôtes, reverse proxy, localhost et contrôle anti-CSRF OAuth. Les tests d’identité Discord, de récompense unique et d’autorisation admin existants passent.

9 contrôles dans un vrai Chromium 153, avec deux origines HTTPS distinctes (parent 127.0.0.1, iframe localhost), certificats temporaires et réponse OAuth simulée côté serveur de test : l’ancien cookie Strict est bloqué ; le cookie partitionné est conservé ; authentification puis rechargement conservent le joueur ; tutoriel et récompense unique restent corrects ; suppression des cookies puis nouvelle identification retrouvent le même profil sans nouveau gain. Le caractère HttpOnly, Secure, SameSite=None et la clé de partition sont vérifiés dans le navigateur.

38 contrôles navigateur admin et 24 contrôles tutoriel sur PC, fenêtre Discord basse et mobile, sans erreur JavaScript. CRC des archives et reconstruction du ZIP extrait. Les données de test sont temporaires. Le serveur de simulation se trouve uniquement dans les tests et n’est pas importé par la passerelle livrée.

## Limites
Le défaut des cookies est reproduit et corrigé localement ; ce résultat ne prouve pas que tous les réglages de votre hébergement ou de votre application Discord sont corrects. Le lancement réel dans votre Activity reste à confirmer après déploiement. Aucun accès Coolify/GitHub authentifié, aucun secret et aucune donnée de production n’ont été utilisés. Les avatars de vrais joueurs et l’économie Gold commune Oddium/PostgreSQL ne sont pas testés : l’adaptateur existant conserve son économie SQLite isolée. Le tutoriel et les trois identifiants admin autorisés restent inchangés.
