#!/bin/bash

echo "Choisis l'utilisateur pour les commits :"
echo "1) Claire M"
echo "2) Aude M"
echo "3) Doha A"
echo "4) Nicolas R"
read -p "➡️  Ton choix (1/2/3/4) : " choix

case "$choix" in
  1)
    git config user.name "Claire M"
    git config user.email "claire.martin@telecom-sudparis.eu"
    echo "✅ Config Git pour Claire appliquée"
    ;;
  2)
    git config user.name "Aude M"
    git config user.email "aude.mesmin@gmail.com"
    echo "✅ Config Git pour Aude appliquée"
    ;;
  3)
    git config user.name "Doha A"
    git config user.email "doha.aberkane@yahoo.com"
    echo "✅ Config Git pour Doha appliquée"
    ;;
  4)
    git config user.name "Nicolas R"
    git config user.email "ncls.rdl@outlook.fr"
    echo "✅ Config Git pour Nicolas appliquée"
    ;;
  *)
    echo "❌ Choix invalide"
    ;;
esac

# Affiche la config actuelle
echo -e "\n📄 Configuration actuelle :"
git config user.name
git config user.email
