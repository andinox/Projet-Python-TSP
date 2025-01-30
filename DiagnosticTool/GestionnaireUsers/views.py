from django.contrib.auth.forms import PasswordResetForm, AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate,logout
from django.views.generic import View
from . import forms


# class LoginPageView(View):
#     form_class = forms.LoginForm
#     def get(self, request):
#         form = self.form_class()
#         message = ''
#         return render(request, self.template_name, context={'form': form, 'message': message})
#
#     def post(self, request):
#         form = self.form_class(request.POST)
#         if form.is_valid():
#             user = authenticate(
#                 username=form.cleaned_data['username'],
#                 password=form.cleaned_data['password'],
#             )
#             if user is not None:
#                 login(request, user)
#                 return redirect('home')
#         message = 'Identifiants invalides.'
#         return render(request, self.template_name, context={'form': form, 'message': message})

def logout_user(request):
    """
    function that logout a user
    :param request:
    :return: login page
    """
    logout(request)
    return redirect('login_page')


def password_reset_form(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('password_reset_done')
    else:
        form = PasswordResetForm()
    return render(request, 'GestionnaireUsers/registration/password_reset_form.html', {'form': form})

def password_reset_done(request):
    return render(request, 'GestionnaireUsers/registration/password_reset_done.html')

def password_reset_confirm(request):
    # Logique pour confirmer la réinitialisation du mot de passe avec un token
    return render(request, 'GestionnaireUsers/registration/password_reset_confirm.html')

def password_reset_complete(request):
    return render(request, 'GestionnaireUsers/registration/password_reset_complete.html')