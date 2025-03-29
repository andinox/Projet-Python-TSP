from django.views.generic import ListView
from django.shortcuts import redirect
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

    def get(self, request, *args, **kwargs):
        # Checks if a slug is passed in the URL to redirect
        selected_slug = request.GET.get('scenario')
        if selected_slug:
            scenario = Scenario.objects.get(slug=selected_slug)
            return redirect(reverse('scenario', kwargs={'slug': scenario.slug}))

        return super().get(request, *args, **kwargs)
