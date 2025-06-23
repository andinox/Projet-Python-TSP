from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView
from core.models import Diagnostic, Router
from core.models.scenario import Scenario
from core.diagnostic_scenarios.internet_connection_loss import InternetConnectionLossDiagnostic
import logging

logger = logging.getLogger(__name__)

class ScenarioDetailView(LoginRequiredMixin, DetailView):
    """
    This class-based view displays the details of a given scenario
    """
    model = Scenario
    template_name = "core/scenario_details.html"
    context_object_name = "scenario"
    slug_url_kwarg = 'slug'  # The URL parameter is 'slug'
    login_url = 'login_page'

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
        
        # Pass diagnostic_result if it exists
        if hasattr(self, 'diagnostic_result'):
            context['diagnostic_result'] = self.diagnostic_result
        else:
            context['diagnostic_result'] = None

        # Retrieve and remove 'diagnostic_launched' flag from session to show the alert only once
        diagnostic_launched = self.request.session.pop('diagnostic_launched', False)
        context['diagnostic_launched'] = diagnostic_launched

        return context

    def post(self, request, *args, **kwargs):
        """
        This method handles the POST request
        """

        # we take the scenario object matching with the url
        scenario = self.get_object()

        # here we call the class corresponding to the requested scenario &
        # run the diagnostic algo adapted according to the slug
        if scenario.slug == 'perte-de-connexion-vers-internet':
            logger.info("Starting internet connection loss diagnostic")
            diagnostic = Diagnostic.objects.create(
                router=Router.objects.get(),
                diagnosis_type="Perte de connexion vers internet",
                result=""
            )  # Assuming only one router, hence get()

            dgc_result = InternetConnectionLossDiagnostic(diagnostic)  # dgc = diagnostic
            logger.info(f"Diagnostic result info: {dgc_result}")
            diagnostic_result = dgc_result.run()
            diagnostic.result = diagnostic_result
            diagnostic.save()  # Save the diagnostic result to the DB

            # Store the result to pass it to the template
            self.diagnostic_result = diagnostic_result
            self.object = scenario

            # Set a session flag to display the alert after redirect
            request.session['diagnostic_launched'] = True

        elif scenario.slug == '...':
            # TODO: Implement other scenarios and call their diagnostic functions
            pass

        return self.render_to_response(self.get_context_data(object=scenario))
