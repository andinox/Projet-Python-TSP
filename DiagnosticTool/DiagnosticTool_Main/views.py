from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'DiagnosticTool_Main/home.html')


def scenario(request):
    return 1