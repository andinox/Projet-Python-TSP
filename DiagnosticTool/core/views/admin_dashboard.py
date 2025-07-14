from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from core.models import *

# Decorator to restrict access to superusers only
def superuser_required(view_func):
    decorated_view_func = user_passes_test(
        lambda u: u.is_active and u.is_superuser,  # checks if user is active and superuser
        login_url='/admin/login/'                  # and redirect to admin login if check fails
    )(view_func)
    return decorated_view_func

@method_decorator(superuser_required, name='dispatch')
class AdminDashboardView(TemplateView):
    template_name = 'core/admin_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # raw data queries with related foreign keys to optimize queries
        interfaces_conf = Interface_CONF.objects.select_related('router').all()
        interfaces_test = Interface_TEST.objects.select_related('router').all()
        bgp_conf = BGP_CONF.objects.select_related('router').all()
        bgp_test = BGP_TEST.objects.select_related('router').all()
        arp_conf = ARP_CONF.objects.select_related('idinterface').all()
        arp_test = ARP_TEST.objects.select_related('idinterface').all()
        diagnostics = Diagnostic.objects.select_related('router').all()
        scenarios = Scenario.objects.all()

        # calculates statistics for summary display
        interfaces_test_unreachable = sum(1 for i in interfaces_test if not i.reachability)
        interfaces_test_reachable = sum(1 for i in interfaces_test if i.reachability)
        interfaces_admin_up = sum(1 for i in interfaces_test if i.admin_status == 'up')
        interfaces_admin_down = sum(1 for i in interfaces_test if i.admin_status == 'down')
        bgp_test_down = sum(1 for b in bgp_test if b.up_down_status == 'DOWN')

        # injection of data and statistics into the context for template rendering
        context.update({
            'interfaces_conf': interfaces_conf,
            'interfaces_test': interfaces_test,
            'bgp_conf': bgp_conf,
            'bgp_test': bgp_test,
            'arp_conf': arp_conf,
            'arp_test': arp_test,
            'diagnostics': diagnostics,
            'scenarios': scenarios,

            # stats for display
            'interfaces_test_unreachable': interfaces_test_unreachable,
            'interfaces_test_reachable': interfaces_test_reachable,
            'interfaces_admin_up': interfaces_admin_up,
            'interfaces_admin_down': interfaces_admin_down,
            'bgp_test_down': bgp_test_down,
        })

        return context
