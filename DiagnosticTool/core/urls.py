from django.urls import path
from core.views import *
from core.views import scenarios
from core.views.home import home

urlpatterns = [
    path('home/', home, name='home'),
    path('scenario/<slug:slug>/', scenarios.scenario_details, name='scenario'),
]