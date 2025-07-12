from core.models import Diagnostic
from core.diagnostic_scenarios import BasicNetworkTests
from core.models.bgp import BGP_TEST
from core.scripts import ping
    
class IntranetConnectionLossDiagnostic:
    """
    Diagnostic class for analyzing intranet connection issues,
    focusing on the status of BGP sessions with neighboring routers.
    """
    
    def __init__(self, diagnostic:Diagnostic):
        self.diagnostic = diagnostic
        self.router = diagnostic.router
        self.tests=BasicNetworkTests(router=self.diagnostic.router)


    def run(self):
        """
        Returns:
            A string report summarizing the BGP neighbors' status, 
            including ASN, state, and time since last change.
        """

        report = []

        # Basic network tests
        issue_found, basic_tests_report = self.tests.run_all_basic_tests()
        report.append(basic_tests_report)

        if issue_found:
            return "\n".join(report)
        
        # BGP analysis
        report.append("\n----- DÉBUT DU DIAGNOSTIC : Perte de connexion Intranet -----\n")
        bgp_entries = BGP_TEST.objects.filter(router=self.router)

        for entry in bgp_entries:
            report.append(f"Voisin : {entry.neighbor_ip}")
            report.append(f"ASN distant : {entry.asn}")
            report.append(f"Statut : {entry.up_down_status}")
            report.append(f"Dernier changement d’état : Le {entry.timestamp.date()} à {entry.timestamp.time().strftime('%H:%M:%S')}")

            if entry.up_down_status.lower() == "up":
                report.append("Diagnostic : session BGP stable avec le voisin\n")

                if ping("10.255.255.1",5,2,"192.168.68.8"):
                    report.append("[OK] ping vers le serveur de l'entreprise réussi.")
                    report.append("Demander une analyse plus pousser pour comprendre à quel niveau est le problème")
                else :
                    report.append("[ECHEC] Le ping vers le serveur de l'entreprise a échoué")
                    report.append("Problème détecté au niveau du lien BGP")

            else:
                report.append("Diagnostic : session BGP inactive, vérifier la configuration et la connectivité\n")

        return "\n".join(report)