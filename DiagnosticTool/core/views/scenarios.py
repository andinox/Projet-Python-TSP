from django.views.generic import DetailView
from core.models.scenario import Scenario

class ScenarioDetailView(DetailView):
    """
    This class-based view displays the details of a given scenario
    """
    model = Scenario
    template_name = "core/scenario_details.html"
    context_object_name = "scenarios"
    slug_url_kwarg = 'slug'  # The URL parameter is 'slug'

    def get_object(self):
        """
        This method returns the object corresponding to the given slug
        """
        return Scenario.objects.get(slug=self.kwargs['slug'])
