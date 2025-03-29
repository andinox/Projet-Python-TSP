from django.urls import path
from core.views import scenarios, home

urlpatterns = [
    path('home/', home, name='home'),
    path('scenario/<slug:slug>/', scenarios.ScenarioDetailView, name='scenario'),
]