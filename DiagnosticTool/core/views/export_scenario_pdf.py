from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView
from django.template.loader import get_template
import tempfile
from core.models import Diagnostic


class ScenarioPDFView(LoginRequiredMixin, DetailView):
    model = Diagnostic
    pk_url_kwarg = "pk"

    def get(self, request, *args, **kwargs):
        return self.generate_pdf()

    def post(self, request, *args, **kwargs):
        return self.generate_pdf()

    def generate_pdf(self):
        from weasyprint import HTML

        diagnostic = self.get_object()
        scenario = diagnostic.get_scenario_name()
        router = diagnostic.router
        created_at = diagnostic.date

        template = get_template("core/pdf_template.html")
        html_string = template.render(
            {
                "scenario": scenario,
                "diagnostic": diagnostic,
                "router": router,
                "created_at": created_at,
            }
        )

        html = HTML(string=html_string)
        result = tempfile.NamedTemporaryFile(delete=True, suffix=".pdf")
        html.write_pdf(result.name)
        result.seek(0)

        return HttpResponse(
            result.read(),
            content_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="rapport_{diagnostic.diagnosis_type}_{diagnostic.date}.pdf"'
            },
        )
