from django.views.generic import DetailView
import environ as env
from core.models import Diagnostic, Router
from core.models.scenario import Scenario
from core.diagnostic_scenarios.basic_network_tests import BasicNetworkTests
from core.diagnostic_scenarios.intranet_connection_loss import IntranetConnectionLossDiagnostic

from core.diagnostic_scenarios.internet_connection_loss import (
    InternetConnectionLossDiagnostic,
)
import logging

logger = logging.getLogger(__name__)


class ScenarioDetailView(DetailView):
    """
    This class-based view displays the details of a given scenario
    """

    model = Scenario
    template_name = "core/scenario_details.html"
    context_object_name = "scenario"
    slug_url_kwarg = "slug"  # The URL parameter is 'slug'

    def get_object(self):
        """
        This method returns the object corresponding to the given slug
        """
        return Scenario.objects.get(slug=self.kwargs["slug"])

    def get_context_data(self, **kwargs):
        """
        This method returns the context data; it prepares data that will be passed to the template scenario_details.html
        """
        context = super(ScenarioDetailView, self).get_context_data(**kwargs)
        if hasattr(
            self, "diagnostic_result"
        ):  # diagnostic_results will be used in template & it stocks results of self
            context["diagnostic_result"] = self.diagnostic_result
        else:
            context["diagnostic_result"] = None
        return context

    def post(self, request, *args, **kwargs):
        """
        This method handles the POST request
        """

        # we take the scenario object matching with the url
        scenario = self.get_object()

        # diagnostic creation
        logger.info(f"Début du diagnostic pour le scénario : {scenario.slug}")
        diagnostic = Diagnostic.objects.create(
            router=Router.objects.get(), diagnosis_type=scenario.slug, result=""
        )  # here we only have one router that's why I only do a get

        # we test first with BasicNetworkTests before going any further
        basic_tests = BasicNetworkTests(router=diagnostic.router)
        interfaces_report = basic_tests.report_interfaces_status()

        if "down" in interfaces_report or "admin down" in interfaces_report:
            logger.info("Interfaces KO, scénario interrompu")
            diagnostic.result = (
                interfaces_report
                + "\n\nScénario interrompu : les interfaces ne sont pas en état opérationnel."
            )
            diagnostic.save()
            self.diagnostic_result = diagnostic.result
            self.object = scenario
            return self.render_to_response(self.get_context_data(object=scenario))

        logger.info("Interfaces OK, poursuite du scénario")

        # here we call the class corresponding to the requested scenario &
        # run the diagnostic algo adapted according to the slug
        if scenario.slug == "perte-de-connexion-vers-internet":
            dgc_result = InternetConnectionLossDiagnostic(diagnostic)
            diagnostic_result = dgc_result.run()
            logger.info(f"Résultat du diagnostic :\n{diagnostic_result}")
            dgc_result = InternetConnectionLossDiagnostic(
                diagnostic
            )  # dgc = diagnostic
            diagnostic.result = diagnostic_result
            diagnostic.save()  # we save in DB the result of the diagnostic
            self.diagnostic_result = diagnostic_result
            self.object = scenario

        elif scenario.slug == "perte-de-connexion-vers-les-sites-de-lentreprise":
            logger.info("[BGP - DIAGNOSTIC]")
            dgc_result = IntranetConnectionLossDiagnostic(diagnostic)
            diagnostic_result = dgc_result.run()
            logger.info(f"Résultat du diagnostic Intranet :\n{diagnostic_result}")
            diagnostic.result = diagnostic_result
            diagnostic.save()
            self.diagnostic_result = diagnostic_result
            self.object = scenario

        elif scenario.slug == "...":
            # TODO do same for the others scenarios &
            # need to call the implemented function
            pass
        return self.render_to_response(self.get_context_data(object=scenario))
