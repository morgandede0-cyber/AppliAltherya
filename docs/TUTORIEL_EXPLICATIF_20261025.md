# Tutoriel exclusivement explicatif

Les douze scènes et le design validé sont conservés. Les pages expliquent les fonctions du jeu sans les ouvrir : aucun menu, aucune navigation de lieu et aucune manipulation du joueur ne sont demandés.

Commandes : Commencer, Suivant, Précédent et Terminer. La dernière page donne la récompense normale uniquement si elle n’a pas déjà été reçue. La relecture conserve sa commande de fermeture.

Le code de visite des menus, les observateurs de boutons et le bandeau de retour ont été supprimés du client. Les anciennes requêtes tutorial_visit sont acceptées comme opérations sans effet pour la compatibilité des clients/tests anciens ; elles n’enregistrent plus de visite et ne débloquent rien.

Le serveur ne réclame plus de visite pour avancer ou terminer. Il conserve la validation de l’étape courante, les transactions, l’identité Discord et les reçus. Le joueur doit toujours parcourir séquentiellement les douze pages. Une requête répétée ne saute pas une page et ne donne pas une seconde récompense.

La progression courante est conservée même sans visite enregistrée ; elle reprend après déconnexion. La révision obligatoire wolf-twelve-required-20261024-v1 ne change pas : aucun nouveau reset. Les Gold, XP, quêtes, inventaire, prix des outils, hotbarres et livres restent inchangés.

## Vérifications

- 32 tests serveur tutoriel, identité et révision : réussis.
- 254 tests client, dont parcours sans visite, bouton Précédent, relecture, changement de compte et reprise sur erreur : réussis.
- 404 contrôles navigateur en 1440×900, 1186×570, 390×844 et 320×568 : douze pages, absence de menu et de changement de scène pendant le tuto, précédent, rechargement, récompense et relecture. Aucune erreur JavaScript ni asset manquant.
- Compilation Python API/bot et TypeScript/Vite : réussies. Les avertissements de taille du bundle et d’import audio déjà présents restent non bloquants.
- Contrôle visuel interne des pages sur PC/mobile ; aucun changement d’illustration.

Les tests utilisent une base temporaire et des comptes fictifs. Aucun accès à la base de production ou à Oddium, aucun message Discord réel ni déploiement n’a été effectué.

## Installation

Mise à jour cumulative à copier sur le projet existant, puis reconstruire et redéployer le frontend et l’API dans Coolify. Conserver les variables d’environnement et la base de données. Recharger l’Activity après déploiement pour charger le nouveau client.

Cette correction remplace le fonctionnement de visite décrit dans les documents de tutoriel précédents, conservés comme historique.
