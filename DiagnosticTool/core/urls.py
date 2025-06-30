from django.urls import path

from core.views import HomeView
from core.views.scenarios import *
from core.views.export_scenario_pdf import *

urlpatterns = [
    path('home/', HomeView.as_view(), name='home'),
    path('scenario/<slug:slug>/', ScenarioDetailView.as_view(), name='scenario'),
    path('diagnostic/<int:pk>/export/', ScenarioPDFView.as_view(), name='export_diagnostic_pdf'),
]