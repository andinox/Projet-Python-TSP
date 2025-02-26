from django.urls import path
from core.views import scenarios
from core.views.home import *

urlpatterns = [
    path('home/', home, name='home'),
    path('scenario/<slug:slug>/', scenarios.scenario_details, name='scenario'),
]