from celery import shared_task
from core.models import Diagnostic
from core.diagnostic_scenarios.internet_connection_loss import InternetConnectionLossDiagnostic

@shared_task
def run_internet_connection_loss_diagnostic(diagnostic_id):
    diagnostic = Diagnostic.objects.get(id=diagnostic_id)
    diag = InternetConnectionLossDiagnostic(diagnostic)
    result = diag.run()
    diagnostic.result = result
    diagnostic.save()
