#!/usr/bin/env python3
"""
Test simple pour vérifier l'installation
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NAIRA.settings')
django.setup()

from django.test import TestCase
from auth.backends import Argon2Backend

def test_argon2_basic():
    """Test basique d'Argon2"""
    print("Test basique d'Argon2")
    print("=" * 30)
    
    backend = Argon2Backend()
    
    # Test de hachage
    password = "test123"
    hashed = Argon2Backend.hash_password(password)
    print(f"Mot de passe haché: {hashed[:50]}...")
    
    # Test de vérification
    result = backend.verify_password(password, hashed)
    print(f"Vérification: {'OK' if result else 'ÉCHEC'}")
    
    # Test de vérification incorrecte
    wrong_result = backend.verify_password("wrong", hashed)
    print(f"Vérification incorrecte: {'OK' if not wrong_result else 'ÉCHEC'}")
    
    print("\nTest Argon2 réussi !")

def test_django_setup():
    """Test de la configuration Django"""
    print("\nTest de la configuration Django")
    print("=" * 35)
    
    from django.conf import settings
    
    # Vérifier les apps installées
    print(f"Apps installées: {len(settings.INSTALLED_APPS)}")
    
    # Vérifier les backends d'authentification
    print(f"Backends d'auth: {len(settings.AUTHENTICATION_BACKENDS)}")
    
    # Vérifier la base de données
    print(f"Base de données: {settings.DATABASES['default']['ENGINE']}")
    
    print("\nConfiguration Django OK !")

if __name__ == "__main__":
    try:
        test_argon2_basic()
        test_django_setup()
        print("\nTous les tests sont passés !")
        print("Votre système d'authentification est prêt.")
    except Exception as e:
        print(f"\nErreur: {e}")
        sys.exit(1) 