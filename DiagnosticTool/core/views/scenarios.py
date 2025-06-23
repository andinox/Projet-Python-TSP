from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView

from core.models import Diagnostic, Router
from core.models.scenario import Scenario
from core.diagnostic_scenarios.basic_network_tests import BasicNetworkTests

from core.diagnostic_scenarios.internet_connection_loss import (
    InternetConnectionLossDiagnostic,
)
from core.diagnostic_scenarios.intranet_connection_loss import IntranetConnectionLossDiagnostic
import logging

logger = logging.getLogger(__name__)


class ScenarioDetailView(LoginRequiredMixin, DetailView):
    """
    This class-based view displays the details of a given scenario
    """

    model = Scenario
    template_name = "core/scenario_details.html"
    context_object_name = "scenario"
    slug_url_kwarg = 'slug'
    login_url = 'login_page'

    def get_object(self):
        """
        This method returns the object corresponding to the given slug
        """
        return Scenario.objects.get(slug=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        """
        This method returns the context data; it prepares data that will be passed to the template
        """
        context = super().get_context_data(**kwargs)

        # Pass diagnostic_result if it exists
        context['diagnostic_result'] = getattr(self, 'diagnostic_result', None)

        # Retrieve and remove 'diagnostic_launched' flag from session
        context['diagnostic_launched'] = self.request.session.pop('diagnostic_launched', False)

        return context

    def post(self, request, *args, **kwargs):
        """
        This method handles the POST request
        """

        # Get scenario instance from slug
        scenario = self.get_object()

        logger.info(f"Début du diagnostic pour le scénario : {scenario.slug}")

        # Create diagnostic object (assuming only one router)
        router = Router.objects.get()
        diagnostic = Diagnostic.objects.create(
            router=router,
            diagnosis_type=scenario.slug,
            result=""
        )


        # Run basic network tests before launching the full diagnostic
        basic_tests = BasicNetworkTests(router=router)
        interfaces_report = basic_tests.report_interfaces_status()

        if "down" in interfaces_report or "admin down" in interfaces_report:
            logger.info("Interfaces KO, scénario interrompu")
            diagnostic.result = (
                interfaces_report +
                "\n\nScénario interrompu : les interfaces ne sont pas en état opérationnel."
            )
            diagnostic.save()
            self.diagnostic_result = diagnostic.result
            self.object = scenario
            return self.render_to_response(self.get_context_data(object=scenario))

        logger.info("Interfaces OK, poursuite du scénario")

        # Dispatch based on scenario slug
        if scenario.slug == 'perte-de-connexion-vers-internet':
            logger.info("Starting internet connection loss diagnostic")
            dgc = InternetConnectionLossDiagnostic(diagnostic)
            diagnostic_result = dgc.run()
            logger.info(f"Résultat du diagnostic :\n{diagnostic_result}")
            diagnostic.result = diagnostic_result
            diagnostic.save()
            self.diagnostic_result = diagnostic_result
            self.object = scenario

        elif scenario.slug == "perte-de-connexion-vers-les-sites-de-lentreprise":
            logger.info("[BGP - DIAGNOSTIC]")
            dgc = IntranetConnectionLossDiagnostic(diagnostic)
            diagnostic_result = dgc.run()
            logger.info(f"Résultat du diagnostic Intranet :\n{diagnostic_result}")
            diagnostic.result = diagnostic_result
            diagnostic.save()
            self.diagnostic_result = diagnostic_result
            self.object = scenario


        elif scenario.slug == "diagnostiquer-tous-les-scenarios-ci-dessus":
            logger.info("[DIAGNOSTIC GÉNÉRAL]")
            results=[]
            diagnostic_instance = diagnostic
            diagnostics = [InternetConnectionLossDiagnostic(diagnostic),IntranetConnectionLossDiagnostic(diagnostic)]
            for d in diagnostics:
                result = d.run()
                logger.info(f"Résultat du diagnostic :\n{result}")
                results.append(result)
            all_results = "\n".join(results)
            diagnostic_instance.result = all_results
            diagnostic_instance.save()
            self.diagnostic_result = all_results
            self.object = scenario

        elif scenario.slug == "...":
            # TODO: Implement other scenarios and call their diagnostic functions
            self.object = scenario

        # Set session flag to show alert once
        request.session['diagnostic_launched'] = True

        return self.render_to_response(self.get_context_data(object=scenario))
