# Application `core`

Cette application constitue le cœur fonctionnel du projet **DiagnosticTool**. Elle regroupe l'ensemble de la logique de diagnostic réseau ainsi que les modèles et vues associés.

## Contenu principal

- `diagnostic_scenarios/` : différents scénarios de tests réseau (perte de connexion, sécurité, tests basiques...).
- `models/` : modèles Django représentant routeurs, interfaces, tables ARP, sessions BGP, etc.
- `router/` : fonctions de connexion et de traitement des données récupérées sur les équipements.
- `views/` : vues Django permettant d'afficher la page d'accueil, le tableau de bord administrateur ou encore le détail d'un scénario.
- `scripts/` : scripts utilisés pour interagir avec les routeurs ou recevoir les données envoyées par Telegraf.
- `management/commands/` : commandes personnalisées pour lancer des diagnostics depuis la ligne de commande.
- `templates/` : gabarits HTML spécifiques à l'application.
- `telegraf/` : fichiers de configuration pour la collecte d'informations via Telegraf.

En centralisant ces éléments, le dossier `core` gère la récupération des données réseau, leur stockage en base et la génération des rapports affichés dans l'interface web.
