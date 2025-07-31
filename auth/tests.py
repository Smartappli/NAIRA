"""
Tests pour l'authentification Django avec Argon2
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User, Group
from django.urls import reverse
from auth.backends import Argon2Backend
from auth.models import Profile
import json


class Argon2BackendTest(TestCase):
    """Tests pour le backend d'authentification Argon2"""

    def setUp(self):
        """Configuration initiale"""
        self.backend = Argon2Backend()
        self.client = Client()
        
        # Créer un utilisateur de test
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password=None
        )
        # Hasher le mot de passe avec Argon2
        self.user.password = Argon2Backend.hash_password('testpass123')
        self.user.save()
        
        # Récupérer le profil existant (créé automatiquement)
        self.profile = Profile.objects.get(user=self.user)
        self.profile.email = 'test@example.com'
        self.profile.is_verified = True
        self.profile.save()

    def test_hash_password(self):
        """Test du hachage de mot de passe"""
        password = "secret123"
        hashed = Argon2Backend.hash_password(password)
        
        # Vérifier que le hash commence par $argon2
        self.assertTrue(hashed.startswith('$argon2'))
        
        # Vérifier que le hash est différent du mot de passe original
        self.assertNotEqual(password, hashed)

    def test_verify_password_correct(self):
        """Test de vérification de mot de passe correct"""
        password = "secret123"
        hashed = Argon2Backend.hash_password(password)
        
        result = self.backend.verify_password(password, hashed)
        self.assertTrue(result)

    def test_verify_password_incorrect(self):
        """Test de vérification de mot de passe incorrect"""
        password = "secret123"
        wrong_password = "wrongpass"
        hashed = Argon2Backend.hash_password(password)
        
        result = self.backend.verify_password(wrong_password, hashed)
        self.assertFalse(result)

    def test_authenticate_username_success(self):
        """Test d'authentification avec username"""
        user = self.backend.authenticate(
            request=None,
            username='testuser',
            password='testpass123'
        )
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'testuser')

    def test_authenticate_email_success(self):
        """Test d'authentification avec email"""
        user = self.backend.authenticate(
            request=None,
            username='test@example.com',
            password='testpass123'
        )
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'test@example.com')

    def test_authenticate_wrong_password(self):
        """Test d'authentification avec mauvais mot de passe"""
        user = self.backend.authenticate(
            request=None,
            username='testuser',
            password='wrongpass'
        )
        self.assertIsNone(user)

    def test_authenticate_nonexistent_user(self):
        """Test d'authentification avec utilisateur inexistant"""
        user = self.backend.authenticate(
            request=None,
            username='nonexistent',
            password='testpass123'
        )
        self.assertIsNone(user)

    def test_get_user(self):
        """Test de récupération d'utilisateur par ID"""
        user = self.backend.get_user(self.user.id)
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'testuser')

    def test_get_nonexistent_user(self):
        """Test de récupération d'utilisateur inexistant"""
        user = self.backend.get_user(99999)
        self.assertIsNone(user)


class AuthViewsTest(TestCase):
    """Tests pour les vues d'authentification"""

    def setUp(self):
        """Configuration initiale"""
        self.client = Client()
        self.register_url = '/auth/register/'
        self.login_url = '/auth/login/'
        self.logout_url = '/auth/logout/'

    def test_register_page_loads(self):
        """Test que la page d'inscription se charge"""
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Register')

    def test_login_page_loads(self):
        """Test que la page de connexion se charge"""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login')

    def test_register_success(self):
        """Test d'inscription réussie"""
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpass123'
        }
        response = self.client.post(self.register_url, data)
        
        # Vérifier que l'utilisateur a été créé
        user = User.objects.get(username='newuser')
        self.assertEqual(user.email, 'new@example.com')
        
        # Vérifier que le profil a été créé
        profile = Profile.objects.get(user=user)
        self.assertEqual(profile.email, 'new@example.com')

    def test_register_duplicate_username(self):
        """Test d'inscription avec username existant"""
        # Créer un utilisateur existant
        User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='pass123'
        )
        
        data = {
            'username': 'existinguser',
            'email': 'new@example.com',
            'password': 'newpass123'
        }
        response = self.client.post(self.register_url, data)
        
        # Vérifier que l'utilisateur n'a pas été créé
        users = User.objects.filter(username='existinguser')
        self.assertEqual(users.count(), 1)

    def test_login_success(self):
        """Test de connexion réussie"""
        # Créer un utilisateur
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password=None
        )
        user.password = Argon2Backend.hash_password('testpass123')
        user.save()
        
        data = {
            'email-username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, data, follow=True)
        
        # Vérifier que la redirection a eu lieu (code 200 après redirection)
        self.assertEqual(response.status_code, 200)

    def test_login_with_email(self):
        """Test de connexion avec email"""
        # Créer un utilisateur
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password=None
        )
        user.password = Argon2Backend.hash_password('testpass123')
        user.save()
        
        data = {
            'email-username': 'test@example.com',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, data, follow=True)
        
        # Vérifier que la redirection a eu lieu (code 200 après redirection)
        self.assertEqual(response.status_code, 200)

    def test_login_wrong_password(self):
        """Test de connexion avec mauvais mot de passe"""
        # Créer un utilisateur
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password=None
        )
        user.password = Argon2Backend.hash_password('testpass123')
        user.save()
        
        data = {
            'email-username': 'testuser',
            'password': 'wrongpass'
        }
        response = self.client.post(self.login_url, data, follow=True)
        
        # Vérifier que l'utilisateur n'est pas connecté
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class AuthAPITest(TestCase):
    """Tests pour l'API d'authentification"""

    def setUp(self):
        """Configuration initiale"""
        self.client = Client()
        self.api_signup_url = '/auth/api/signup/'
        self.api_login_url = '/auth/api/login/'
        self.api_logout_url = '/auth/api/logout/'
        self.api_profile_url = '/auth/api/profile/'

    def test_api_signup_success(self):
        """Test d'inscription API réussie"""
        data = {
            'username': 'apiuser',
            'email': 'api@example.com',
            'password': 'apipass123'
        }
        response = self.client.post(
            self.api_signup_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        
        # Vérifier que l'utilisateur a été créé
        user = User.objects.get(username='apiuser')
        self.assertEqual(user.email, 'api@example.com')

    def test_api_signup_duplicate_username(self):
        """Test d'inscription API avec username existant"""
        # Créer un utilisateur existant
        User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='pass123'
        )
        
        data = {
            'username': 'existinguser',
            'email': 'new@example.com',
            'password': 'newpass123'
        }
        response = self.client.post(
            self.api_signup_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])

    def test_api_login_success(self):
        """Test de connexion API réussie"""
        # Créer un utilisateur
        user = User.objects.create_user(
            username='apiuser',
            email='api@example.com',
            password=None
        )
        user.password = Argon2Backend.hash_password('apipass123')
        user.save()
        
        data = {
            'login': 'apiuser',
            'password': 'apipass123'
        }
        response = self.client.post(
            self.api_login_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])

    def test_api_login_with_email(self):
        """Test de connexion API avec email"""
        # Créer un utilisateur
        user = User.objects.create_user(
            username='apiuser',
            email='api@example.com',
            password=None
        )
        user.password = Argon2Backend.hash_password('apipass123')
        user.save()
        
        data = {
            'login': 'api@example.com',
            'password': 'apipass123'
        }
        response = self.client.post(
            self.api_login_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])

    def test_api_login_wrong_password(self):
        """Test de connexion API avec mauvais mot de passe"""
        # Créer un utilisateur
        user = User.objects.create_user(
            username='apiuser',
            email='api@example.com',
            password=None
        )
        user.password = Argon2Backend.hash_password('apipass123')
        user.save()
        
        data = {
            'login': 'apiuser',
            'password': 'wrongpass'
        }
        response = self.client.post(
            self.api_login_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 401)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])

    def test_api_profile_authenticated(self):
        """Test de récupération de profil API (utilisateur connecté)"""
        # Créer et connecter un utilisateur
        user = User.objects.create_user(
            username='apiuser',
            email='api@example.com',
            password=None
        )
        user.password = Argon2Backend.hash_password('apipass123')
        user.save()
        
        # Connecter l'utilisateur
        self.client.force_login(user)
        
        response = self.client.get(self.api_profile_url)
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['user']['username'], 'apiuser')

    def test_api_profile_unauthenticated(self):
        """Test de récupération de profil API (utilisateur non connecté)"""
        response = self.client.get(self.api_profile_url)
        
        self.assertEqual(response.status_code, 401)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])

    def test_api_logout(self):
        """Test de déconnexion API"""
        # Créer et connecter un utilisateur
        user = User.objects.create_user(
            username='apiuser',
            email='api@example.com',
            password=None
        )
        user.password = Argon2Backend.hash_password('apipass123')
        user.save()
        
        # Connecter l'utilisateur
        self.client.force_login(user)
        
        response = self.client.post(self.api_logout_url)
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])


class ProfileModelTest(TestCase):
    """Tests pour le modèle Profile"""

    def setUp(self):
        """Configuration initiale"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_profile_creation(self):
        """Test de création de profil"""
        # Le profil est créé automatiquement avec l'utilisateur
        profile = Profile.objects.get(user=self.user)
        
        self.assertEqual(profile.user, self.user)
        self.assertIsNotNone(profile)

    def test_profile_str_representation(self):
        """Test de la représentation string du profil"""
        profile = Profile.objects.get(user=self.user)
        
        self.assertEqual(str(profile), f'Profile de {self.user.username}')

    def test_profile_default_values(self):
        """Test des valeurs par défaut du profil"""
        profile = Profile.objects.get(user=self.user)
        
        # Vérifier les valeurs par défaut
        self.assertFalse(profile.is_verified)
        self.assertIsNone(profile.email_token)
        self.assertIsNone(profile.forget_password_token) 