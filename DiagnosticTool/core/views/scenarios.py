from django.views.generic import DetailView
from core.models.scenario import Scenario
from core.diagnostic_scenarios.internet_connection_loss import InternetConnectionLossDiagnostic
import logging
logger = logging.getLogger(__name__)


class ScenarioDetailView(DetailView):
    """
    This class-based view displays the details of a given scenario
    """
    model = Scenario
    template_name = "core/scenario_details.html"
    context_object_name = "scenario"
    slug_url_kwarg = 'slug'  # The URL parameter is 'slug'

    def get_object(self):
        """
        This method returns the object corresponding to the given slug
        """
        return Scenario.objects.get(slug=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        """
        This method returns the context data; it prepares data that will be passed to the template scenario_details.html
        """
        context = super(ScenarioDetailView, self).get_context_data(**kwargs)
        if hasattr(self, 'diagnostic_result'):#diagnostic_results will be used in template & it stocks results of self
            context['diagnostic_result'] = self.diagnostic_result
        else:
            context['diagnostic_result'] = None
        return context

    def post(self, request, *args, **kwargs):
        """
        This method handles the POST request
        """

        #we take the scenario object matching with the url
        scenario = self.get_object()

        #here we call the class corresponding to the requested scenario &
        #run the diagnostic algo adapted according to the slug
        if scenario.slug =='perte-de-connexion-vers-internet':
	    logger.info("Début du diagnostic perte de connexion vers internet")
            dgc_result = InternetConnectionLossDiagnostic(scenario) #dgc = diagnostic
	    logger.info("info dgc_result:{}".format(dgc_result))
            self.diagnostic_result = dgc_result.run()

        elif scenario.slug =='...':
            #TODO do same for the others scenarios &
            # need to call the implemented function
            pass
        return self.render_to_response(self.get_context_data(object=scenario))



"""




"""
