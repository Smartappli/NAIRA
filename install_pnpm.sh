#!/bin/bash

echo "Installation de pnpm pour le projet NAIRA"
echo "==========================================="

# Vérifier si Node.js est installé
if ! command -v node &> /dev/null; then
    echo "Node.js n'est pas installé. Veuillez l'installer d'abord."
    echo "   Visitez: https://nodejs.org/"
    exit 1
fi

echo "Node.js est installé"

# Vérifier si pnpm est déjà installé
if command -v pnpm &> /dev/null; then
    echo "pnpm est déjà installé"
    pnpm --version
else
    echo "Installation de pnpm..."
    
    # Méthode 1: Via npm (recommandé)
    if command -v npm &> /dev/null; then
        echo "   Installation via npm..."
        npm install -g pnpm
        if [ $? -eq 0 ]; then
            echo "pnpm installé avec succès via npm"
        else
            echo "Échec de l'installation via npm"
            echo "   Tentative avec curl..."
            
            # Méthode 2: Via curl (fallback)
            curl -fsSL https://get.pnpm.io/install.sh | sh -
            if [ $? -eq 0 ]; then
                echo "pnpm installé avec succès via curl"
                # Recharger le shell pour avoir accès à pnpm
                export PATH="$HOME/.local/share/pnpm:$PATH"
            else
                echo "Échec de l'installation de pnpm"
                echo "   Veuillez l'installer manuellement:"
                echo "   https://pnpm.io/installation"
                exit 1
            fi
        fi
    else
        echo "npm n'est pas installé"
        echo "   Installation via curl..."
        curl -fsSL https://get.pnpm.io/install.sh | sh -
        if [ $? -eq 0 ]; then
            echo "pnpm installé avec succès via curl"
            export PATH="$HOME/.local/share/pnpm:$PATH"
        else
            echo "Échec de l'installation de pnpm"
            echo "   Veuillez l'installer manuellement:"
            echo "   https://pnpm.io/installation"
            exit 1
        fi
    fi
fi

echo ""
echo "pnpm est prêt à être utilisé !"
echo ""
echo "Commandes utiles :"
echo "   pnpm install    # Installer les dépendances"
echo "   pnpm dev        # Démarrer le serveur de développement"
echo "   pnpm build      # Build de production"
echo "   pnpm preview    # Prévisualiser le build"
echo ""
echo "Pour démarrer le frontend :"
echo "   ./start_frontend.sh" 