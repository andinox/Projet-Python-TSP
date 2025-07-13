from core.models import Diagnostic
from core.diagnostic_scenarios.basic_network_tests import BasicNetworkTests
from core.models.bgp import BGP_TEST, BGP_CONF
from core.scripts import ping
from datetime import timedelta
from django.utils.timezone import now
from django.db.models import Max

    
class IntranetConnectionLossDiagnostic:
    """
    Diagnostic class for analyzing intranet connection issues,
    focusing on the status of BGP sessions with neighboring routers.
    """
    
    def __init__(self, diagnostic:Diagnostic):
        self.diagnostic = diagnostic
        self.router = diagnostic.router
        self.tests=BasicNetworkTests(router=self.diagnostic.router)

    def compare_bgp_conf_and_test(self):
        """
        Compare BGP_CONF avec la dernière entrée BGP_TEST (par voisin).
        Retourne un rapport textuel des différences.
        """
        messages = []
        differences = 0

        # BGP_CONF: what's exepected
        conf_entries = {
            (entry.neighbor_ip, entry.asn, entry.up_down_status.strip().lower())
            for entry in BGP_CONF.objects.filter(router=self.router)
        }

        # BGP_TEST: last entries based on neighbor_ip
        latest_test_entries = []
        neighbors = (
            BGP_TEST.objects.filter(router=self.router)
            .values("neighbor_ip")
            .annotate(latest=Max("timestamp"))
        )

        for n in neighbors:
            entry = BGP_TEST.objects.filter(
                router=self.router,
                neighbor_ip=n["neighbor_ip"],
                timestamp=n["latest"]
            ).first()
            if entry:
                latest_test_entries.append(entry)

        test_entries = {
            (entry.neighbor_ip, entry.asn, entry.up_down_status.strip().lower())
            for entry in latest_test_entries
        }

        # Différences
        for missing in conf_entries - test_entries:
            ip, asn, status = missing
            messages.append(f"[DIFF] BGP_CONF {ip} ASN {asn} ({status}) non trouvé dans les dernières entrées BGP_TEST.")
            differences += 1

        for extra in test_entries - conf_entries:
            ip, asn, status = extra
            messages.append(f"[INFO] BGP_TEST {ip} ASN {asn} ({status}) n'existe pas dans BGP_CONF (peut être normal).")

        # Résumé
        if differences == 0:
            messages.append("[INFO] Toutes les sessions BGP attendues sont présentes dans les tests récents.")
        else:
            messages.append(f"[RÉSUMÉ] {differences} différences trouvées entre BGP_CONF et dernières entrées BGP_TEST.")

        return messages



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
        report.append("\nDÉBUT DU DIAGNOSTIC : Perte de connexion Intranet\n")
        bgp_entries = BGP_TEST.objects.filter(router=self.router)
        report.append("\n[Comparaison BGP initialement configuré et configuration actuelle du BGP]")
        report.extend(self.compare_bgp_conf_and_test())
        for entry in bgp_entries:
            report.append(f"Voisin : {entry.neighbor_ip}")
            report.append(f"ASN distant : {entry.asn}")
            report.append(f"Statut : {entry.up_down_status}")
            report.append(f"Dernier changement d’état : Le {entry.timestamp.date()} à {entry.timestamp.time().strftime('%H:%M:%S')}")

            if entry.up_down_status.lower() == "up":
                report.append("Diagnostic : session BGP stable avec le voisin\n")

                if ping("10.255.255.1",5,2,"192.168.68.8"):
                    report.append("[OK] ping vers le serveur de l'entreprise réussi.")
                    report.append("Demander une analyse plus poussée pour comprendre à quel niveau est le problème")
                else :
                    report.append("[ECHEC] Le ping vers le serveur de l'entreprise a échoué")
                    report.append("Problème détecté au niveau du lien BGP")

            else:
                report.append("Diagnostic : session BGP inactive, vérifier la configuration et la connectivité\n")

        return "\n".join(report)