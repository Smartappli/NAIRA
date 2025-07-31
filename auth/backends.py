"""
Backend d'authentification personnalisé pour Django avec Argon2
"""

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from argon2 import PasswordHasher, exceptions

class Argon2Backend(BaseBackend):
    """
    Backend d'authentification personnalisé utilisant Argon2 pour le hachage des mots de passe
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authentifie un utilisateur avec username/email et mot de passe
        """
        if username is None or password is None:
            return None
        
        # Rechercher l'utilisateur par username ou email
        try:
            if '@' in username:
                # Si c'est un email, chercher par email
                user = User.objects.get(email=username)
            else:
                # Sinon, chercher par username
                user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None
        
        # Vérifier si l'utilisateur est actif
        if not user.is_active:
            return None
        
        # Vérifier le mot de passe avec Argon2
        if self.verify_password(password, user.password):
            return user
        
        return None
    
    def get_user(self, user_id):
        """
        Récupère un utilisateur par son ID
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
    
    def verify_password(self, password, hashed_password):
        """
        Vérifie un mot de passe avec Argon2
        """
        try:
            ph = PasswordHasher()
            ph.verify(hashed_password, password)
            return True
        except exceptions.VerifyMismatchError:
            return False
        except Exception:
            return False
    
    @staticmethod
    def hash_password(password):
        """
        Hashe un mot de passe avec Argon2
        """
        ph = PasswordHasher()
        return ph.hash(password) 