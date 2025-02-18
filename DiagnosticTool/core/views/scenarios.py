from django.shortcuts import render, redirect
from core.models.scenario import Scenario

def scenario_details(request,slug):
    """
    fonction qui va afficher les détails d'un scénario donné
    """
    scenario = Scenario.objects.get(slug=slug)
    return render(request, 'core/scenario_details.html', {'scenario': scenario})


