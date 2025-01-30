from django.urls import path
from . import views
urlpatterns = [

    path('home', views.home, name='home'),
    path('scenario', views.scenario, name='scenario'),

]
