from django.urls import path
from django.contrib.auth.views import LoginView
from . import views

urlpatterns = [
    path('', LoginView.as_view(template_name='GestionnaireUsers/registration/login.html',redirect_authenticated_user=True), name='login_page'),
    path('logout', views.logout_user, name='logout_page'),

    path('login/password_reset/', views.password_reset_form, name='password_reset_form'),
    path('login/password_reset_done/', views.password_reset_done, name='password_reset_done'),
    path('login/password_reset_confirm/', views.password_reset_confirm, name='password_reset_confirm'),
    path('login/password_reset_complete/', views.password_reset_complete, name='password_reset_complete'),


]
