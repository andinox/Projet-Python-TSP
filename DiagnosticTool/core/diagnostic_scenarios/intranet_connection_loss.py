from core.models import Diagnostic, Router
from core.diagnostic_scenarios.basic_network_tests import BasicNetworkTests
from core.models.bgp import BGP_TEST, BGP_CONF

def format_duration(seconds_str):
    """
    Converts a duration expressed as a string into a human-readable format: 'X h Y min Z sec'.
    If the input is invalid, returns 'inconnu', which means 'unknown' in French.
    """

    try:
        seconds = int(seconds_str.strip().split()[0])
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60

        if hours > 0:
            return f"{hours} h {minutes} min {seconds} sec"
        elif minutes > 0:
            return f"{minutes} min {seconds} sec"
        else:
            return f"{seconds} sec"
    except:
        return "inconnu"
    
class IntranetConnectionLossDiagnostic:
    """
    Diagnostic class for analyzing intranet connection issues,
    focusing on the status of BGP sessions with neighboring routers.
    """
    
    def __init__(self, diagnostic:Diagnostic):
        self.diagnostic = diagnostic
        self.router = diagnostic.router
        self.tests=BasicNetworkTests(router=self.diagnostic.router)


    def render_report(self):
        """
        Returns:
            A string report summarizing the BGP neighbors' status, 
            including ASN, state, and time since last change.
        """
        lines = ["[BGP - DIAGNOSTIC]\n"]

        bgp_entries = BGP_TEST.objects.filter(router=self.router)

        for entry in bgp_entries:
            lines.append(f"Voisin : {entry.neighbor_ip}")
            lines.append(f"ASN distant : {entry.asn}")
            lines.append(f"Statut : {entry.up_down_status}")
            lines.append(f"Dernier changement d’état : {format_duration(entry.time_last_change)}")

            if entry.up_down_status.lower() == "up":
                lines.append("Diagnostic : session BGP stable avec le voisin\n")
            else:
                lines.append("Diagnostic : session BGP inactive, vérifier la configuration et la connectivité\n")

        return "\n".join(lines)