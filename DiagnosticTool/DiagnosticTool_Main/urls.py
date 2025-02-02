from django.urls import path
from . import views
urlpatterns = [


#jpense utiliser les pk pour les redirections des liens pour les pages des scenarios
    path('home', views.home, name='home'),
    path('perteCoInternet', views.perteConnexionInternet, name='perteCoInternet'),
    path('perteCoEntreprise', views.perteConnexionEntreprise, name='perteCoEntreprise'),
    path('tempsLatElevee', views.tempsLatenceElevee, name='tempsLatElevee'),

]
