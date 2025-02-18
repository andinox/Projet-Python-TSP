from django.shortcuts import render, redirect
from core.models.scenario import Scenario


def home(request):
    if request.method == 'POST':
        # Récupérer le slug du scénario sélectionné
        selected_slug = request.POST.get('scenario')
        if selected_slug:
            # Récupérer le scénario correspondant au slug
            scenario = Scenario.objects.get(slug=selected_slug)
            # Rediriger vers la page de détails du scénario
            return redirect('scenario', slug=scenario.slug)
    
    scenarios = Scenario.objects.all()
    return render(request, 'core/home.html', {'scenarios': scenarios})
    #scenarios = Scenario.objects.all()
    #print(scenarios)
    #return render(request, 'core/home.html', {'scenarios': scenarios})


def scenario_details(request,slug):
    """
    fonction qui va afficher les détails d'un scénario donné
    """
    scenario = Scenario.objects.get(slug=slug)
    return render(request, 'core/scenario_details.html', {'scenario': scenario})


