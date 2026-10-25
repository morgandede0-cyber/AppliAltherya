# Passages latéraux des lieux de quête

Les accès au Bureau des convois, aux Archives de la banque, à la Halte de la Lisière, à l’Atelier des sceaux, au Relais de la Pierre Fendue et au Belvédère des Veilleurs quittent la rangée des actions.

Une flèche à droite permet d’entrer dans le lieu débloqué. Le nom est masqué par défaut et apparaît uniquement au survol avec une souris. Sur écran tactile, seule la flèche est visible ; son nom reste disponible aux lecteurs d’écran. Le retour depuis ces six scènes utilise la même flèche inversée sur la gauche. Les boutons de service, de dialogue et d’action restent dans leur rangée. Les autres retours, dont Retour à Legacy depuis le marchand, restent inchangés.

L’asset vectoriel quest-exit-right.svg est partagé entre les deux directions. L’affichage utilise toujours can_enter fourni par le serveur : aucune condition de niveau ou d’histoire n’est contournée. Les passages sont masqués pendant le tutoriel et avec les autres interactions lorsqu’un menu est ouvert.

Vérifications : 9 tests ciblés du monde de quête et du journal ; compilation TypeScript/Vite ; test navigateur isolé du véritable composant de scène avec routage simulé, sur 1440×900, 1186×570, 390×844 et 320×568. Les 48 accès aller/retour des six lieux sont contrôlés, ainsi que le chargement du SVG. Les tests unitaires vérifient le masquage des accès verrouillés et la conservation des commandes de service.

Cette archive est cumulative : appliquer au projet existant, reconstruire puis redéployer. Aucun changement de base de données, de récompense ou de prix. Aucun déploiement public effectué.
