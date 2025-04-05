from django.views.generic import ListView
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from core.models.scenario import Scenario

class HomeView(ListView):
    """
    This class-based view displays the available scenarios.
    When a scenario is clicked, it redirects the user to the selected scenario's details page
    """
    model = Scenario
    template_name = "core/home.html"
    context_object_name = "scenarios"

    def post(self, request, *args, **kwargs):
        selected_slug = request.POST.get('scenario')
        if selected_slug:
            scenario = get_object_or_404(Scenario, slug=selected_slug)
            return redirect(reverse('scenario', kwargs={'slug': scenario.slug}))
        return redirect('home')

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
