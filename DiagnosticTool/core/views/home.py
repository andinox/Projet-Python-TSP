from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse

from core.models import Diagnostic
from core.models.scenario import Scenario
from django.utils import timezone
from datetime import timedelta

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

class DiagnosticHistory:
    @staticmethod
    def get_diagnostic_history_last_30d(user, days=30):
        since = timezone.now() - timedelta(days=days)
        if user.is_superuser: #if admin user than view of all the history
            return Diagnostic.objects.filter(date__gte=since).select_related('router').order_by('-date')
        else: #else the user can check only theirs
            return Diagnostic.objects.filter(created_by=user, date__gte=since).select_related('router').order_by(
                '-date')
class HomeView(LoginRequiredMixin,ListView):
    """
    This class-based view displays the available scenarios.
    Only accessible if user is logged in
    When a scenario is clicked, it redirects the user to the selected scenario's details page
    """
    model = Scenario
    template_name = "core/home.html"
    context_object_name = "scenarios"
    login_url = 'login_page'

    def post(self, request, *args, **kwargs):
        selected_slug = request.POST.get('scenario')
        if selected_slug:
            scenario = get_object_or_404(Scenario, slug=selected_slug)
            return redirect(reverse('scenario', kwargs={'slug': scenario.slug}))
        return redirect('home')



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        diagnostics_history = DiagnosticHistory.get_diagnostic_history_last_30d(user=self.request.user)

        paginator = Paginator(diagnostics_history, 3)
        page = self.request.GET.get('page')
        try:
            diagnostics_page = paginator.page(page)
        except PageNotAnInteger:
            diagnostics_page = paginator.page(1)
        except EmptyPage:
            diagnostics_page = paginator.page(paginator.num_pages)

        context['diagnostic_history'] = diagnostics_page
        return context