from core.models import Diagnostic, Router
from core.scripts.basic_functions import ping, traceroute
from core.diagnostic_scenarios.basic_network_tests import BasicNetworkTests


class InternetConnectionLossDiagnostic:
    
    def __init__(self, diagnostic:Diagnostic):
        self.diagnostic = diagnostic
        self.tests=BasicNetworkTests(router=self.diagnostic.router)

    def get_next_hop(self):
        """
        Returns the next hop from the router
        """
        return self.diagnostic.router.next_hop

    def run(self):
        """
        Runs the tests for internet connection loss by using the decision tree
        """
        report = []

        # interface status check
        interfaces_report = self.tests.report_interfaces_status()
        report.append(interfaces_report)

        # need to call get_next_hop
        # ping towards google.com
        report.append("ping vers google.com en cours...")
        if ping("google.com"):
            report.append("OK ping vers google.com réussi; issue causée par accès à extranet")
            report.append("ticket doit être créé pour signaler le problème")
            return "\n".join(report)
        else:
            # ping towards 8.8.8.8
            report.append("NOK ping vers google.com échoué; test de ping à faire vers 8.8.8.8")
            if ping("8.8.8.8"):
                report.append("OK ping vers 8.8.8.8 réussi; problème DNS détecté")
                report.append("ticket pour vérifier la résolution DNS")
                return "\n".join(report)
            else:
                # traceroute towards 8.8.8.8
                report.append("ping vers 8.8.8.8 échoué; exécution d’un traceroute...")
                hops, last_hop = traceroute("8.8.8.8")
                if last_hop:
                    report.append(f"OK traceroute réussi; dernier hop atteint : {last_hop}")
                    next_hop = self.get_next_hop()
                    if next_hop:
                        report.append("problème de connectivité détecté, analyse du dernier hop nécessaire")
                        report.append("ticket pour investigation")
                        if ping(next_hop):
                            report.append(f"OK ping vers next_hop {next_hop} est réussi !")
                        else:
                            report.append(f"NOK ping vers next_hop {next_hop} a échoué ...")
                else:
                    report.append("NOK traceroute échoué;  impossible de déterminer le dernier hop")
                    report.append("ticket pour investigation approfondie")
                return "\n".join(report)
