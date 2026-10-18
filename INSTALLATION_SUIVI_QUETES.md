# Suivi des quêtes à droite — 17 octobre 2026

Le « Journal de route » se trouve à droite de l’écran, sous le nom du lieu. Son bouton « Quêtes » ouvre ou replie le panneau. Le choix est mémorisé sur l’appareil. Sur mobile et dans une fenêtre basse, il commence replié en l’absence de choix enregistré.

- Histoire : prochain chapitre verrouillé, objets encore manquants, accès au marché Histoire et au troubadour.
- Quotidien : compteurs réels du serveur, trois objectifs par page, état de la récompense et accès au château.
- Missions : contrat et expédition en cours, accès aux menus correspondants.

Le panneau est caché pendant le chargement, le tutoriel obligatoire et l’ouverture d’un menu. Ses données se mettent à jour avec les réponses aux actions et la synchronisation serveur existante (toutes les 15 secondes quand aucune opération n’est en cours). Il n’ajoute aucun prélèvement ni récompense côté client.

## Installer
Extraire le correctif léger à la racine du projet existant, ou utiliser le dossier Altherya_V0_8_10 de l’archive complète. Effectuer la mise à jour Git habituelle puis redéployer dans Coolify. Fermer et rouvrir l’Activity après le déploiement. Conserver le .env et le volume de données actuels.

## Périmètre
Le suivi est fonctionnel pour les données déjà exposées par le jeu. Le nouveau scénario « Les routes des Trois Terres » reste un document séparé : son moteur de quêtes et ses nouvelles missions ne sont pas intégrés par ce correctif. Le panneau n’affiche pas de compteurs inventés pour ce scénario.

Aucune modification des positions des boutons du hub, des textes officiels de l’histoire, de l’API ou de la base de données. Aucun changement de port ni de secret Discord.
