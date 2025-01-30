from django.shortcuts import render

from DiagnosticTool_Main.models import Scenario


def home(request):
    scenarios = Scenario.objects.all()
    print(scenarios)
    return render(request, 'DiagnosticTool_Main/home.html', {'scenarios': scenarios})


def scenario(request):
    return 1