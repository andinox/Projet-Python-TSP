from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView

from core.models import Diagnostic, Router
from core.models.scenario import Scenario
from core.diagnostic_scenarios.basic_network_tests import BasicNetworkTests

from core.diagnostic_scenarios.internet_connection_loss import (
    InternetConnectionLossDiagnostic,
)
from core.diagnostic_scenarios.intranet_connection_loss import IntranetConnectionLossDiagnostic
from core.diagnostic_scenarios.security_scenario import SecurityDiagnostic

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

    def get_queryset(self):
        """
        Returns the base queryset for retrieving Scenario objects; can be extended with select_related or prefetch_related for optimization.
        """
        return Scenario.objects.all()
    
    def get_context_data(self, **kwargs):
        """
        This method returns the context data; it prepares data that will be passed to the template
        """
        context = super().get_context_data(**kwargs)

        # Pass diagnostic_result if it exists
        context['diagnostic_result'] = getattr(self, 'diagnostic_result', None)

        # Retrieve and remove 'diagnostic_launched' flag from session
        context['diagnostic_launched'] = self.request.session.pop('diagnostic_launched', False)
        
        context['diagnostic'] = getattr(self, 'diagnostic', None)

        return context

    def post(self, request, *args, **kwargs):
        """
        This method handles the POST request
        """

        # Get scenario instance from slug
        scenario = self.get_object()

        logger.info(f"Début du diagnostic pour le scénario : {scenario.slug}")

        #prefetch datas
        try:
            router=Router.objects.prefetch_related(
                "bgp_tests",
                "bgp_confs",
                "interface_tests",
                "interface_confs"
            ).select_related("user").get(user=request.user)
        except Router.DoesNotExist:
            logger.error("Aucun routeur trouvé en base de données.")
            return self.render_to_response(self.get_context_data(object=scenario))
        
        # Create diagnostic object (assuming only one router)
        diagnostic = Diagnostic.objects.create(
            router=router,
            diagnosis_type=scenario.slug,
            result=""
        )

        # Dispatch based on scenario slug
        diagnostic_result=""
        if scenario.slug == 'perte-de-connexion-vers-internet':
            logger.info("Starting internet connection loss diagnostic")
            dgc = InternetConnectionLossDiagnostic(diagnostic)
            diagnostic_result = dgc.run()

        elif scenario.slug == "perte-de-connexion-vers-les-sites-de-lentreprise":
            logger.info("Starting intranet connection loss diagnostic")
            dgc = IntranetConnectionLossDiagnostic(diagnostic)
            diagnostic_result = dgc.run()

        elif scenario.slug == "je-souhaite-verifier-la-securite-de-mon-reseau":
            logger.info("[DIAGNOSTIC DE SÉCURITÉ]")
            dgc = SecurityDiagnostic(router)
            diagnostic_result = dgc.run()

        elif scenario.slug == "diagnostiquer-tous-les-scenarios-ci-dessus":
            logger.info("[DIAGNOSTIC GÉNÉRAL]")
            results=[]
            diagnostics = [InternetConnectionLossDiagnostic(diagnostic),IntranetConnectionLossDiagnostic(diagnostic),SecurityDiagnostic(diagnostic)]
            for d in diagnostics:
                result = d.run()
                logger.info(f"Résultat du diagnostic :\n{result}")
                results.append(result)
                if any(keyword in result.upper() for keyword in ["ÉCHEC", "ECHEC", "ERREUR"]):
                    logger.error("Un échec ou une erreur a été détecté. Interruption du diagnostic global.")
                    break
            diagnostic_result="\n".join(results)
        else:
            logger.warning("Scénario non reconnu : aucune action lancée.")
       
       
        logger.info(f"Résultat final du diagnostic ({scenario.slug}) :\n{diagnostic_result}")

        diagnostic.result = diagnostic_result
        diagnostic.save()

        self.diagnostic = diagnostic
        self.diagnostic_result = diagnostic_result
        self.object = scenario
        request.session['diagnostic_launched'] = True

        return self.render_to_response(self.get_context_data(object=scenario))