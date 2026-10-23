# Remise immédiate des quêtes — 24 octobre 2026

Une quête dont tous les objectifs sont terminés peut désormais être rendue immédiatement auprès du destinataire indiqué. Le serveur ne vérifie plus de durée minimale globale avant le paiement. Le bouton de remise n’affiche plus de compte à rebours et ignore une ancienne valeur de délai éventuellement encore en cache.

Ce changement s’applique aussi aux quêtes déjà acceptées, sans reset ni modification des sauvegardes. Le champ de compatibilité claim_at vaut désormais zéro.

Les missions et analyses encore en cours conservent leurs durées. Les objectifs doivent tous être terminés ; le lieu de remise, la révision de progression, les paliers de niveau, les montants déjà configurés et les reçus empêchant un deuxième paiement restent contrôlés.

## Vérification

- Compilation Python API/bot et compilation TypeScript / Vite réussies.
- 39 tests serveur de campagne réussis, dont remise immédiate d’une quête récemment acceptée et une seule récompense lors de demandes concurrentes.
- 217 tests d’interface réussis, dont bouton actif malgré une ancienne date de remise future, limites de niveau et délais des travaux de terrain.
- 52 contrôles navigateur réussis sur l’application compilée avec API locale et base temporaire, en 1440×900 et 390×844. La première quête est rendue dans les secondes suivant son acceptation ; la progression et le montant réellement ajouté au portefeuille sont vérifiés. Les missions longues restent bloquées jusqu’à leur échéance. Aucune erreur JavaScript relevée.

Aucun déploiement ni changement de données en production. Cette archive cumulative conserve les six assets et toutes les modifications de la précédente livraison.

## Installation

Copier le contenu de Altherya_V0_8_10 dans votre projet existant, accepter les remplacements et ajouter les nouveaux fichiers, puis reconstruire et redéployer. Conserver vos assets déjà installés, votre base de données et vos variables d’environnement. Aucun reset nécessaire.
