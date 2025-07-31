#!/usr/bin/env python3
"""
Script pour configurer le PYTHONPATH et résoudre les problèmes d'imports
"""

import os
import sys
from pathlib import Path

def setup_python_path():
    """Configure le PYTHONPATH pour le projet Django"""
    
    # Obtenir le chemin du projet
    project_root = Path(__file__).parent.absolute()
    
    # Ajouter le répertoire racine au PYTHONPATH
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    # Ajouter le répertoire NAIRA au PYTHONPATH
    naira_path = project_root / "NAIRA"
    if str(naira_path) not in sys.path:
        sys.path.insert(0, str(naira_path))
    
    # Configurer les variables d'environnement Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NAIRA.settings')
    os.environ.setdefault('PYTHONPATH', str(project_root))
    
    print(f"PYTHONPATH configuré:")
    print(f"  - Projet: {project_root}")
    print(f"  - NAIRA: {naira_path}")
    print(f"  - DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE')}")

if __name__ == "__main__":
    setup_python_path()
    
    # Test des imports Django
    try:
        import django
        django.setup()
        print("\nDjango configuré avec succès!")
        
        # Test des imports du projet
        from auth.backends import Argon2Backend
        print("Import Argon2Backend: OK")
        
        from auth.models import Profile
        print("Import Profile: OK")
        
        print("\nTous les imports fonctionnent correctement!")
        
    except Exception as e:
        print(f"\nErreur lors de la configuration: {e}")
        sys.exit(1) 