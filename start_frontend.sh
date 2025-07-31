#!/bin/bash

echo "Démarrage du frontend Vue.js 3 pour NAIRA"
echo "=========================================="

# Vérifier si Node.js est installé
if ! command -v node &> /dev/null; then
    echo "Node.js n'est pas installé. Veuillez l'installer d'abord."
    echo "   Visitez: https://nodejs.org/"
    exit 1
fi

# Vérifier si pnpm est installé
if ! command -v pnpm &> /dev/null; then
    echo "pnpm n'est pas installé. Veuillez l'installer d'abord."
    echo "   Installation: npm install -g pnpm"
    echo "   Ou visitez: https://pnpm.io/installation"
    exit 1
fi

echo "Node.js et pnpm sont installés"

# Aller dans le dossier frontend
cd frontend

# Vérifier si node_modules existe
if [ ! -d "node_modules" ]; then
    echo "Installation des dépendances avec pnpm..."
    pnpm install
    if [ $? -ne 0 ]; then
        echo "Erreur lors de l'installation des dépendances"
        exit 1
    fi
    echo "Dépendances installées avec pnpm"
else
    echo "Dépendances déjà installées"
fi

echo ""
echo "🌐 Démarrage du serveur de développement..."
echo "   Le frontend sera accessible sur: http://localhost:3000"
echo "   Assurez-vous que votre serveur Django est démarré sur: http://localhost:8000"
echo ""
echo "   Appuyez sur Ctrl+C pour arrêter le serveur"
echo ""

# Démarrer le serveur de développement
pnpm dev 