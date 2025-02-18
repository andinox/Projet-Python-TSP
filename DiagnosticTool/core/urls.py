from django.urls import path
from core.views.home import *
from core.views.scenarios import *

urlpatterns = [
    path('home', home, name='home'),
    path('scenario/<slug:slug>/', scenario_details, name='scenario'),
]