# DiagnosticTool

![Python](https://img.shields.io/badge/Python-3.12.7-blue?style=flat-square&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.1.2-green?style=flat-square&logo=django&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-27.3.1-blue?style=flat-square&logo=docker&logoColor=white)
![Docker Compose](https://img.shields.io/badge/Docker%20Compose-2.30.1-blue?style=flat-square&logo=docker&logoColor=white)

## Description

Dans les fournisseurs de réseau aux entreprises, les premières personnes contactées en cas d’incident ne sont pas forcément des personnes ayant une base technique fournie. D’autre part, dans notre formation, tout le monde n’est pas intéressé par les réseaux.

C’est pourquoi, nous avons décidé de créer une application pouvant se connecter à tout routeur Cisco (pourquoi pas voir pour détecter la marque du routeur) et permettant à l’utilisateur d’avoir une interface simplifiée pour lancer des commandes. Cela permettrait ainsi aux ingénieurs de ne pas avoir à traiter des demandes simples de clients et à nos camarades à ne pas avoir à apprendre comment écrire une commande.



## Installation

1. Clone le repo:
   ```sh
    git clone https://github.com/andinox/Projet-Python-TSP.git
   ```
2. Build et start les containers Docker:
   ```sh
    docker-compose up --build
   ```


-------- 
## Notre arbre de décision : 
<p align="center">
   <img src="https://github.com/user-attachments/assets/b6c39de0-6b16-438c-a6ff-dd8ba587df0c" alt="Arbre de décision" width="800" />
</p>

<p align="center">
  <img src="https://github.com/user-attachments/assets/9752600d-22a3-46e7-84b6-f7dbe91b9764" alt="DiagnosticTool_logo" width="200" />
</p>

-------- 
## Docker et workflows

### Docker
Les fichiers `Dockerfile` et `docker-compose.yml` permettent de lancer l'application et Telegraf en une seule commande `docker-compose up`.
La version `docker-compose.prod.yml` ajoute PostgreSQL et Nginx pour la production.

### Workflows GitHub
Le dossier `.github/workflows` contient deux actions :
- `docker-image.yml` construit l'image Docker à chaque push ou pull request sur `main`.
- `auto.yml` crée automatiquement un tag et une release à chaque push sur `main`. (marche pas)
 -------- 
## Notre BDD
<p align="center">
   <img width="2520" height="1304" alt="DiagnosticTool_DB" src="https://github.com/user-attachments/assets/bd47aebc-277f-44a4-8623-8c01f14b329b" />
</p>

--------
## ROADMAP 
### Fonctionnalités déjà opérationnelles

- Scénarios de diagnostic prédéfinis (ex : perte d'accès Internet, problème DNS, etc.).
- Parsing intelligent : ajout d'explications claires et pédagogiques pour rendre les résultats accessibles aux non-initiés.
- Identification automatisée du niveau du problème (LAN, WAN, Internet, DNS...).
- Orientation directe vers l’équipe compétente selon la nature du problème.
- Interface web simple accessible sans connaissances techniques.
- Export des résultats en PDF ou logs.
- Utilisation du protocole SNMP pour la collecte de données réseau, compatible avec la majorité des équipements actuels.

---

### Améliorations prévues à court terme

#### Pour une expérience utilisateur plus fluide

- Intégration de questions intermédiaires pour affiner le diagnostic.
- Ajout d’un chatbot pour accompagner l'utilisateur dans la résolution.
- Adaptation dynamique des scénarios en fonction du type d’équipement détecté (routeur, firewall, switch, etc.).
- Prise en compte des topologies spécifiques, comme la redondance ou les routeurs en simple gateway.
- Support des diagnostics liés aux firewalls.
- Ajout de nouveaux scénarios (latence, déconnexion intermittente, erreurs de routage…).

---

### Vision future – vers une supervision intelligente

#### Automatisation et analyses enrichies

- Stockage d’un historique par interface : état admin/oper, débit, erreurs.
- Visualisation via graphiques interactifs (Grafana, Django-chart, ChartJS, etc.) :
  - Monitoring du trafic en temps réel.
  - Suivi des erreurs et interruptions.
- Détection de pannes récurrentes et de patterns comportementaux (ex : coupures à heure fixe).
- Système de notifications automatiques en cas de dépassement de seuils critiques.

---

### Scénarios de cybersécurité avancés

- Vérification de la présence et pertinence des ACLs sur les interfaces critiques.
- Détection des interfaces exposées sans protection suffisante.
- Évaluation du niveau de sécurité via un score visuel (couleur + pourcentage).
- Lancement de scans de configuration pour identifier des vulnérabilités.
- Intégration potentielle d’un système d’alerte sur les CVE connues.
