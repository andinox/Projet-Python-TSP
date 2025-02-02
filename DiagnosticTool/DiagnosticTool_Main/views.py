from django.shortcuts import render

from DiagnosticTool_Main.models import Scenario


def home(request):
    scenarios = Scenario.objects.all()
    print(scenarios)
    return render(request, 'DiagnosticTool_Main/home.html', {'scenarios': scenarios})


def perteConnexionInternet(request):
    return render(request, 'DiagnosticTool_Main/perte_co_internet.html')

def perteConnexionEntreprise(request):
    return render(request, 'DiagnosticTool_Main/perte_co_sites_entreprise.html')


def tempsLatenceElevee(request):
    return render(request, 'DiagnosticTool_Main/temps_latence_elevee.html')


def verificationSecuriteReseau(request):
    return render(request, 'DiagnosticTool_Main/verif_secu_reseau.html')


1