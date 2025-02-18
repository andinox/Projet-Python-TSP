from django.shortcuts import render, redirect
from core.models.scenario import Scenario


def home(request):
    """
    fonction qui va afficher les scenarios dans la page d'accueil
    par la suite elle permettra également de rediriger vers la bonne page du scenario séléctionné
    """
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
