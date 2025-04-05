from django.urls import path

from core.views import HomeView
from core.views.scenarios import *

urlpatterns = [
    path('home/', HomeView.as_view(), name='home'),
    path('scenario/<slug:slug>/', ScenarioDetailView.as_view(), name='scenario'),
]