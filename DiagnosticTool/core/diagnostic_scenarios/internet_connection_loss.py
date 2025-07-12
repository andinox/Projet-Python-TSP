from core.models import Diagnostic
from core.scripts import ping, traceroute
from core.diagnostic_scenarios.basic_network_tests import BasicNetworkTests


class InternetConnectionLossDiagnostic:
    def __init__(self, diagnostic: Diagnostic):
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
        report = ["DÉBUT DU DIAGNOSTIC : Perte de connexion Internet\n\n"]
        # starts with the basic tests
        issue_found, basic_tests_report = self.tests.run_all_basic_tests()
        report.append(basic_tests_report)

        # if no issues were founded then we can continue with the other tests
        if not issue_found :
            # Step 1: ping towards google.com
            report.append("Étape 1 : ping vers google.com...")
            if ping("google.com"):
                report.append("Résultat : OK - ping vers google.com réussi.")
                report.append("Analyse : la connectivité Internet fonctionne correctement.")
                report.append("Action : le problème vient probablement d'un accès extranet ou d'une application spécifique.")
                report.append("=> Créer un ticket pour signaler le problème au niveau extranet.")
                return "\n".join(report)
    
            # Step 2: ping towards 8.8.8.8
            report.append("Résultat : ÉCHEC - ping vers google.com échoué.")
            report.append("Étape 2 : test de ping vers 8.8.8.8...")
            if ping("8.8.8.8"):
                report.append("Résultat : OK - ping vers 8.8.8.8 réussi.")
                report.append("Analyse : le problème vient de la résolution DNS.")
                report.append("=> Créer un ticket pour vérifier la configuration DNS du routeur.")
                return "\n".join(report)
    
            # Step 3: traceroute to 8.8.8.8
            report.append("Résultat : ÉCHEC - ping vers 8.8.8.8 échoué.")
            report.append("Étape 3 : exécution d’un traceroute vers 8.8.8.8...")
    
            hops, last_hop = traceroute("8.8.8.8")
            if last_hop:
                report.append(f"Résultat : OK - traceroute réussi. Dernier hop atteint : {last_hop}")
                next_hop = self.get_next_hop()
                if next_hop:
                    report.append(f"Test complémentaire : ping vers le next hop {next_hop}...")
                    if ping(next_hop):
                        report.append(f"Résultat : OK - ping vers next hop {next_hop} réussi.")
                    else:
                        report.append(f"Résultat : ÉCHEC - ping vers next hop {next_hop} échoué.")
    
                report.append("Analyse : problème de connectivité détecté, analyse du dernier hop nécessaire.")
                report.append("=> Créer un ticket pour investigation.")
            else:
                report.append("Résultat : ÉCHEC - traceroute échoué, impossible de déterminer le dernier hop.")
                report.append("=> Créer un ticket pour investigation approfondie.")
            return "\n".join(report)
            
        return "\n".join(report)
