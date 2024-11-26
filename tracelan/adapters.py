from allauth.account.adapter import DefaultAccountAdapter
from django.http import HttpResponseForbidden


class NoSignupAccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        """
        Empêche la création de nouveaux comptes.
        """
        return False  # Bloque toutes les tentatives d'inscription
