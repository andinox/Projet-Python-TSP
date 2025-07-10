from django.urls import path

from core.views import HomeView
from core.views.scenarios import *
from core.views.export_scenario_pdf import *
from core.views.admin_dashboard import AdminDashboardView

urlpatterns = [
    path('home/', HomeView.as_view(), name='home'),
    path('scenario/<slug:slug>/', ScenarioDetailView.as_view(), name='scenario'),
    path('admin_view/', AdminDashboardView.as_view(), name='admin_view'),
    path('diagnostic/<int:pk>/export/', ScenarioPDFView.as_view(), name='export_diagnostic_pdf'),
]