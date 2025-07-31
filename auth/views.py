from django.views.generic import TemplateView


"""
Vue de base pour l'authentification
"""


class AuthView(TemplateView):
    """Vue de base pour les pages d'authentification"""
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
