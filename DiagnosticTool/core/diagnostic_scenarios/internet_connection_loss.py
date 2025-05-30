from core.models import Diagnostic,Router
from core.scripts.basic_functions import ping, traceroute

class InternetConnectionLossDiagnostic(Diagnostic):

    def get_next_hop(self):
        """
        TODO: check of how getting next hop (I think we need to use next_hop of model Router that's why I imported it here)
        Returns the next hop from the router
        """
        pass

    def run(self):
        """
        TODO: algorithm to test + using get_next_hop
        """
        report = []

        #need to call get_next_hop
        #ping towards google.com
        report.append("ping vers google.com en cours...")
        if ping("google.com"):
            report.append("OK ping vers google.com réussi; issue causée par accès à extranet")
            report.append("ticket doit être créé pour signaler le problème")
            return "\n".join(report)
        else:
            #ping towards 8.8.8.8
            report.append("NOK ping vers google.com échoué; test de ping à faire vers 8.8.8.8")
            if ping("8.8.8.8"):
                report.append("OK ping vers 8.8.8.8 réussi; problème DNS détecté")
                report.append("ticket pour vérifier la résolution DNS")
                return "\n".join(report)
            else:
                #traceroute towards 8.8.8.8
                report.append("ping vers 8.8.8.8 échoué; exécution d’un traceroute...")
                hops, dernier_hop = traceroute("8.8.8.8")
                if dernier_hop:
                    report.append(f"OK traceroute réussi; dernier hop atteint : {dernier_hop}")
                    report.append("problème de connectivité détecté, analyse du dernier hop nécessaire")
                    report.append("ticket pour investigation")
                    #TODO: use function get_next_hop ?

                else:
                    report.append("NOK traceroute échoué;  impossible de déterminer le dernier hop")
                    report.append("ticket pour investigation approfondie")
                return "\n".join(report)

