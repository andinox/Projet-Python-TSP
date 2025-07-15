from django import forms
from .models import Profile


class LoginForm(forms.Form):
    username = forms.CharField(max_length=120, label="Nom d’utilisateur")
    password = forms.CharField(
        max_length=63, widget=forms.PasswordInput, label="Mot de passe"
    )


class AvatarUploadForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["avatar"]
