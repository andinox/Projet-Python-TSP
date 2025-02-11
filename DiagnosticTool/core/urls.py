from django.urls import path
from . import views
urlpatterns = [


#jpense utiliser les pk pour les redirections des liens pour les pages des scenarios
    path('home', views.home, name='home'),
    path('scenario/<slug:slug>/', views.scenario_details, name='scenario'),

    #path('perteCoEntreprise', views.perteConnexionEntreprise, name='perteCoEntreprise'),
    #path('tempsLatElevee', views.tempsLatenceElevee, name='tempsLatElevee'),
]