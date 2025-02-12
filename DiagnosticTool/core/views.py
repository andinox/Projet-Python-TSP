from django.shortcuts import render, redirect
from core.models import Scenario


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
    fonction qui va affichcier les détails d'un scénario donné
    """
    scenario = Scenario.objects.get(slug=slug)
    return render(request, 'core/scenario_details.html', {'scenario': scenario})





"""
def perteConnexionEntreprise(request):
    return render(request, 'core/perte_co_sites_entreprise.html')


def tempsLatenceElevee(request):
    return render(request, 'core/temps_latence_elevee.html')


def verificationSecuriteReseau(request):
    return render(request, 'core/verif_secu_reseau.html')

"""


