from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView
from django.template.loader import get_template
from weasyprint import HTML
import tempfile
from django.utils.timezone import localtime
from core.models import Diagnostic
from core.models.scenario import Scenario

class ScenarioPDFView(LoginRequiredMixin, DetailView):
    model = Scenario
    slug_url_kwarg = 'slug'

    def post(self, request, *args, **kwargs):
        scenario = self.get_object()
        diagnostic = Diagnostic.objects.filter(
            router__isnull=False,
            diagnosis_type=scenario.slug
        ).order_by('-date').first()

        if not diagnostic:
            return HttpResponse("Aucun diagnostic trouvé.", status=404)

        template = get_template("core/pdf_template.html")
        html_string = template.render({
            "scenario": scenario,
            "diagnostic": diagnostic,
            "router": diagnostic.router,
            "created_at": localtime(diagnostic.date)
        })

        html = HTML(string=html_string)
        result = tempfile.NamedTemporaryFile(delete=True, suffix=".pdf")

        html.write_pdf(result.name)

        result.seek(0)
        return HttpResponse(
            result.read(),
            content_type='application/pdf',
            headers={'Content-Disposition': f'attachment; filename="rapport_{scenario.slug}.pdf"'}
        )
