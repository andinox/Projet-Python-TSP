from core.models import Diagnostic, Router
from core.diagnostic_scenarios.basic_network_tests import BasicNetworkTests
from core.models.bgp import BGP_TEST, BGP_CONF

class IntranetConnectionLossDiagnostic:
    
    def __init__(self, diagnostic:Diagnostic):
        self.diagnostic = diagnostic
        self.tests=BasicNetworkTests(router=self.diagnostic.router)

    def get_router_asn(self):
        """
        Retrieve the ASN of the router from the BGP_TEST model.
        """      
        
    def check_asn(self):
        """
        Check if the ASN of the peer matches from the BGP_CONF model.
        Returns True if the ASN matches, False otherwise.
        """        

    def check_bgp_status(self):
        """
        Check the BGP status of the router.
        Returns True if BGP is operational, False otherwise.
        """