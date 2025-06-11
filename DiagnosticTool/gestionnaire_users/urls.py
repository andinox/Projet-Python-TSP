from django.urls import path, reverse_lazy
from django.contrib.auth.views import (
    LoginView, LogoutView,
    PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView
)
from .views import logout_user, user_info

urlpatterns = [
    path('', LoginView.as_view(template_name='gestionnaire_users/registration/login.html', redirect_authenticated_user=True), name='login_page'),
    path('logout/', logout_user, name='logout_page'),

    # Réinitialisation du mot de passe
    path('password_reset/', PasswordResetView.as_view(
        template_name='gestionnaire_users/registration/password_reset_form.html',
        email_template_name='gestionnaire_users/registration/password_reset_email.html',
        success_url=reverse_lazy('password_reset_done'),
    ), name='password_reset_form'),

    path('password_reset_done/', PasswordResetDoneView.as_view(
        template_name='gestionnaire_users/registration/password_reset_done.html'
    ), name='password_reset_done'),

    path('password_reset_confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(
        template_name='gestionnaire_users/registration/password_reset_confirm.html',
        success_url=reverse_lazy('password_reset_complete')
    ), name='password_reset_confirm'),

    path('password_reset_complete/', PasswordResetCompleteView.as_view(
        template_name='gestionnaire_users/registration/password_reset_complete.html'
    ), name='password_reset_complete'),

    path('infoUser/', user_info, name='infoUser'),
]
