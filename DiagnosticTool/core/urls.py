from django.urls import path
from core.views.home import *
from core.views.scenarios import *

urlpatterns = [


#jpense utiliser les pk pour les redirections des liens pour les pages des scenarios
    path('home', home, name='home'),
    path('scenario/<slug:slug>/', scenario_details, name='scenario'),

]