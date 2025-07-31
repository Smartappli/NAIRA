#!/bin/bash

echo "Tests NAIRA - Authentification"
echo "================================"

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour afficher les résultats
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}$2${NC}"
    else
        echo -e "${RED}$2${NC}"
        exit 1
    fi
}

# Test 1: Backend Django
echo -e "\n${BLUE}Test 1: Backend Django${NC}"
echo "------------------------"

# Vérifier que l'environnement virtuel est activé
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo -e "${YELLOW}⚠️  Environnement virtuel non activé${NC}"
    echo "Activation de l'environnement virtuel..."
    source venv/bin/activate
fi

# Exécuter les tests Django
echo "Exécution des tests Django..."
python manage.py test auth.tests -v 2
DJANGO_RESULT=$?
print_result $DJANGO_RESULT "Tests Django"

# Test 2: Frontend Vue.js
echo -e "\n${BLUE}Test 2: Frontend Vue.js${NC}"
echo "------------------------"

# Vérifier que pnpm est installé
if ! command -v pnpm &> /dev/null; then
    echo -e "${RED}pnpm n'est pas installé${NC}"
    echo "Installation de pnpm..."
    ./install_pnpm.sh
fi

# Aller dans le dossier frontend
cd frontend

# Installer les dépendances si nécessaire
if [ ! -d "node_modules" ]; then
    echo "Installation des dépendances frontend..."
    pnpm install
fi

# Exécuter les tests frontend
echo "Exécution des tests frontend..."
pnpm test:run
FRONTEND_RESULT=$?
print_result $FRONTEND_RESULT "Tests Frontend"

# Retourner au dossier racine
cd ..

# Résumé final
echo -e "\n${BLUE}Résumé des tests${NC}"
echo "=================="
echo -e "${GREEN}Tests Django: ${DJANGO_RESULT}${NC}"
echo -e "${GREEN}Tests Frontend: ${FRONTEND_RESULT}${NC}"

if [ $DJANGO_RESULT -eq 0 ] && [ $FRONTEND_RESULT -eq 0 ]; then
    echo -e "\n${GREEN}Tous les tests sont passés !${NC}"
    echo -e "${BLUE}Votre système d'authentification est prêt !${NC}"
else
    echo -e "\n${RED}Certains tests ont échoué${NC}"
    echo -e "${YELLOW}Vérifiez les erreurs ci-dessus${NC}"
    exit 1
fi 