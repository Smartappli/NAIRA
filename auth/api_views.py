"""
Vues API REST pour l'authentification Django avec Argon2
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User, Group
from django.contrib.auth import login, logout
from auth.backends import Argon2Backend
from auth.models import Profile
from auth.helpers import send_verification_email
import json
import uuid

@csrf_exempt
@require_http_methods(["POST"])
def api_signup(request):
    """
    API d'inscription avec Argon2
    """
    try:
        data = json.loads(request.body)
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        if not username or not email or not password:
            return JsonResponse({
                "success": False,
                "message": "Username, email et mot de passe requis"
            }, status=400)

        # Validation basique
        if len(password) < 6:
            return JsonResponse({
                "success": False,
                "message": "Le mot de passe doit contenir au moins 6 caractères"
            }, status=400)
        
        if '@' not in email:
            return JsonResponse({
                "success": False,
                "message": "Format d'email invalide"
            }, status=400)

        # Vérifier si l'utilisateur existe déjà
        if User.objects.filter(username=username).exists():
            return JsonResponse({
                "success": False,
                "message": "Ce nom d'utilisateur est déjà utilisé"
            }, status=400)
        
        if User.objects.filter(email=email).exists():
            return JsonResponse({
                "success": False,
                "message": "Cet email est déjà utilisé"
            }, status=400)

        # Créer l'utilisateur avec Argon2
        user = User.objects.create_user(username=username, email=email, password=None)
        user.password = Argon2Backend.hash_password(password)
        user.save()

        # Ajouter au groupe client
        user_group, created = Group.objects.get_or_create(name="client")
        user.groups.add(user_group)

        # Créer le profil et envoyer l'email de vérification
        token = str(uuid.uuid4())
        profile, created = Profile.objects.get_or_create(user=user)
        profile.email_token = token
        profile.email = email
        profile.save()

        # Envoyer l'email de vérification
        try:
            send_verification_email(email, token)
            email_sent = True
        except Exception as e:
            email_sent = False

        return JsonResponse({
            "success": True,
                               "message": "Utilisateur créé avec succès",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            },
            "email_verification_sent": email_sent
        }, status=201)

    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "message": "Données JSON invalides"
        }, status=400)
    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": f"Erreur lors de l'inscription: {str(e)}"
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def api_login(request):
    """
    API de connexion avec Argon2 (username ou email)
    """
    try:
        data = json.loads(request.body)
        login_field = data.get("login")  # peut être username ou email
        password = data.get("password")

        if not login_field or not password:
            return JsonResponse({
                "success": False,
                "message": "Login et mot de passe requis"
            }, status=400)

        # Utiliser le backend Argon2 pour l'authentification
        backend = Argon2Backend()
        user = backend.authenticate(request, username=login_field, password=password)

        if user is not None:
            # Connecter l'utilisateur
            login(request, user, backend='auth.backends.Argon2Backend')
            
            return JsonResponse({
                "success": True,
                                       "message": "Authentification réussie",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "is_verified": getattr(user.profile, 'is_verified', False)
                }
            })
        else:
            return JsonResponse({
                "success": False,
                "message": "Nom d'utilisateur ou mot de passe invalide"
            }, status=401)

    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "message": "Données JSON invalides"
        }, status=400)
    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": f"Erreur lors de la connexion: {str(e)}"
        }, status=500)

@require_http_methods(["POST"])
def api_logout(request):
    """
    API de déconnexion
    """
    if request.user.is_authenticated:
        logout(request)
        return JsonResponse({
            "success": True,
            "message": "Déconnexion réussie"
        })
    else:
        return JsonResponse({
            "success": False,
            "message": "Aucun utilisateur connecté"
        }, status=401)

@require_http_methods(["GET"])
def api_profile(request):
    """
    API pour récupérer le profil utilisateur
    """
    if not request.user.is_authenticated:
        return JsonResponse({
            "success": False,
            "message": "Utilisateur non connecté"
        }, status=401)

    try:
        profile = request.user.profile
        return JsonResponse({
            "success": True,
            "user": {
                "id": request.user.id,
                "username": request.user.username,
                "email": request.user.email,
                "is_verified": getattr(profile, 'is_verified', False),
                "created_at": request.user.date_joined.isoformat()
            }
        })
    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": f"Erreur lors de la récupération du profil: {str(e)}"
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def api_verify_email(request):
    """
    API pour vérifier l'email
    """
    try:
        data = json.loads(request.body)
        token = data.get("token")

        if not token:
            return JsonResponse({
                "success": False,
                "message": "Token requis"
            }, status=400)

        # Chercher le profil avec ce token
        try:
            profile = Profile.objects.get(email_token=token)
            profile.is_verified = True
            profile.email_token = None
            profile.save()

            return JsonResponse({
                "success": True,
                                       "message": "Email vérifié avec succès"
            })
        except Profile.DoesNotExist:
            return JsonResponse({
                "success": False,
                "message": "Token invalide ou expiré"
            }, status=400)

    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "message": "Données JSON invalides"
        }, status=400)
    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": f"Erreur lors de la vérification: {str(e)}"
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def api_forgot_password(request):
    """
    API pour la récupération de mot de passe
    """
    try:
        data = json.loads(request.body)
        email = data.get("email")

        if not email:
            return JsonResponse({
                "success": False,
                "message": "Email requis"
            }, status=400)

        try:
            user = User.objects.get(email=email)
            profile = user.profile
            
            # Générer un token de récupération
            token = str(uuid.uuid4())
            profile.forget_password_token = token
            profile.save()

            # Envoyer l'email de récupération
            try:
                from auth.helpers import send_password_reset_email
                send_password_reset_email(email, token)
                email_sent = True
            except Exception as e:
                email_sent = False

            return JsonResponse({
                "success": True,
                "message": "Email de récupération envoyé" if email_sent else "Erreur lors de l'envoi de l'email"
            })

        except User.DoesNotExist:
            return JsonResponse({
                "success": False,
                "message": "Aucun utilisateur trouvé avec cet email"
            }, status=404)

    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "message": "Données JSON invalides"
        }, status=400)
    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": f"Erreur lors de la récupération: {str(e)}"
        }, status=500) 