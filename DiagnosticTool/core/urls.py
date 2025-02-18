from django.urls import path
from .views.home import *  #ici on importe toute les fonctions dans notre folder views du fichier views --> on peut faire du cas par cas pour après (2nd rendu) mais là osef
from .views.scenarios import scenario_details
urlpatterns = [
    path('home', home, name='home'),
    path('scenario/<slug:slug>/', scenario_details, name='scenario'),#utilisation des slugs pour les redirections des liens pour les pages des scenarios avec nom user-friendly

]