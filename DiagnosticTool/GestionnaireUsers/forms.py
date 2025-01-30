# authentication/forms.py
from django import forms
from django.contrib.auth.forms import PasswordResetForm as DjangoPasswordResetForm

class LoginForm(forms.Form):
    username = forms.CharField(max_length=120, label='Nom d’utilisateur')
    password = forms.CharField(max_length=63, widget=forms.PasswordInput, label='Mot de passe')

