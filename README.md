# DiagnosticTools

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
    cd DiagnosticTools
    ```
2. Migration des données si besoin (lors de la création des modèles dans models.py ou des modèles se trouvant dans le folder models)
     Commandes : python manage.py makemigrations nomApp 
                 python manage.py migrate nomApp   
3. Accéder à l'application:
     Lancer dans terminal : `python manage.py runserver`
      et se rendre sur `http://localhost:8000`.    
4.
   `/!\ A FAIRE QUAND ON PENSE AVOIR FINI NOTRE PREMIER RENDU POUR TESTER /!\`
Build et start les containers Docker:
    ```sh
    docker-compose up --build
    ```


