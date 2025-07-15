# Projet Django `DiagnosticTool`

Ce dossier contient les fichiers principaux du projet Django. Vous y trouverez notamment le fichier `settings.py` qui regroupe toute la configuration de l'application (base de données, applications installées, paramètres de sécurité, configuration du routeur et service d'envoi de mails).

## Fichiers clés

- `settings.py` : paramètres de configuration du projet.
- `urls.py` : définition des routes principales et inclusion des URLs des applications `core` et `gestionnaire_users`.
- `asgi.py` et `wsgi.py` : points d'entrée pour servir l'application avec ASGI ou WSGI.
- `__init__.py` : marque ce dossier comme un paquet Python.

Ces fichiers définissent l'environnement et les points d'entrée de l'application web `DiagnosticTool`.
