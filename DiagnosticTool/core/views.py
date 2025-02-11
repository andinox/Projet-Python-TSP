from django.shortcuts import render

from core.models import Scenario


def home(request):
    scenarios = Scenario.objects.all()
    print(scenarios)
    return render(request, 'core/home.html', {'scenarios': scenarios})


def perteConnexionInternet(request):
    return render(request, 'core/perte_co_internet.html')

def perteConnexionEntreprise(request):
    return render(request, 'core/perte_co_sites_entreprise.html')


def tempsLatenceElevee(request):
    return render(request, 'core/temps_latence_elevee.html')


def verificationSecuriteReseau(request):
    return render(request, 'core/verif_secu_reseau.html')


1