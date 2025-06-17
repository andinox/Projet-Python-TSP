# basic_network_tests.py

from core.models import Interface_CONF, Interface_TEST
from django.utils.timezone import now
from core.scripts.LANStatus import check_arp_test_has_data,check_arp_ip_in_interface_network,compare_arp_conf_and_test
from core.scripts.basic_functions import ping

class BasicNetworkTests:
    def __init__(self, router=None):
        self.router = router

    def check_interface_status(self, idinterface):
        """
        Check the operational status of an interface.
        returns True if it is operationally up (reachable),
        returns timedelta if admin down (duration since the most recent continuous admin down),
        returns False if link down,
        returns None if no test data.
        """

        # retrieve the latest test entry for the given interface
        latest_test = (
            Interface_TEST.objects.filter(idinterface=idinterface)
            .order_by("-timestamp")
            .first()
        )

        if not latest_test:
            return None

        # reachability and admin status checks
        reachability = (latest_test.reachability or "").strip().lower()
        if reachability == "up":
            return True

        admin_status = (latest_test.admin_status or "").strip().lower()
        if admin_status == "down":
            test_entries = Interface_TEST.objects.filter(
                idinterface=idinterface
            ).order_by("-timestamp")

            down_since = latest_test.timestamp

            # walk back in time through continuous "down" entries
            for entry in test_entries:
                status = (entry.admin_status or "").strip().lower()
                if status != "down":
                    break
                down_since = entry.timestamp

            return now() - down_since

        # if admin is up but reachability is down → possible link issue
        return False

    def format_timedelta(self, delta):
        """
        Format is 'X days HH:MM:SS'
        """
        total_seconds = int(delta.total_seconds())
        days = delta.days
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{days} days {hours:02}:{minutes:02}:{seconds:02}"
    
    def run_arp_tests(self):
        """
        Executes the three ARP checks and returns whether the tests were successful
         as well as the messages associated with the tests
        """
        report_lines = ["\n[ARP] Lancement des vérifications ARP...\n"]
        all_passed = True

        # 1. Vérifier si ARP_TEST contient des données
        status, message = check_arp_test_has_data()
        report_lines.append(message)
        if not status:
            all_passed = False

        # 2. Vérifier si les IP ARP sont dans le bon réseau
        status, messages = check_arp_ip_in_interface_network()
        report_lines.extend(messages)
        if not status:
            all_passed = False

        # 3. Comparer ARP_CONF et ARP_TEST
        messages = compare_arp_conf_and_test()
        report_lines.extend(messages)

        return all_passed, "\n".join(report_lines)

    def report_interfaces_status(self):
        """
        Generate a report of the status of all interfaces.
        """

        interfaces = Interface_CONF.objects.all()
        issues_found = False
        report_lines = []

        for entry in interfaces:
            idinterface = entry.idinterface
            interface_name = entry.interface_name

            # retrieve the latest test entry for the given interface
            latest_test = (
                Interface_TEST.objects.filter(idinterface=idinterface)
                .order_by("-timestamp")
                .first()
            )

            # no test data available for this interface
            if not latest_test:
                continue

            admin_status = (latest_test.admin_status or "").strip().lower()
            reachability = (latest_test.reachability or "").strip().lower()

            result = self.check_interface_status(idinterface)

            # if an issue was found, print details
            if result is not True:
                issues_found = True

                report_lines.append(f"\nInterface : {interface_name} ({idinterface})")
                report_lines.append(f"Admin status : {admin_status}")
                report_lines.append(f"Reachability : {reachability}")

                if result is False:
                    report_lines.append("Status : down")
                    report_lines.append(
                        "Diagnostic : L'interface est DOWN mais est admin UP → Il peut s'agir d'un problème de lien."
                    )
                elif result is None:
                    report_lines.append("Status : Unknown")
                    report_lines.append(
                        "Diagnostic: Aucune donnée de test ou impossibilité de déterminer depuis quand l'interface est admin down."
                    )
                else:
                    formatted = self.format_timedelta(result)
                    report_lines.append("Status : admin down")
                    report_lines.append(f"Diagnostic : l'interface est admin down depuis {formatted}")

        # no issues found, print success message
        if not issues_found:
            report_lines.append("[INTERFACES] tests effectués avec succès, aucun problème à signaler.")

        return issues_found, "\n".join(report_lines)
    
    def run_all_basic_tests(self):
        """
        Runs the full sequence of tests: interface status → ARP checks → LAN IP ping.

        Returns:
            issue_found (bool): True if any problem was detected during the tests.
            report (str): Full report of the diagnostic process.
        """
        full_report = []
        issue_found = False

        # Step 1: Interface status
        interfaces_issue, interface_report = self.report_interfaces_status()
        full_report.append(interface_report)

        if interfaces_issue:
            issue_found = True
            full_report.append("\n[INFO] Interface issues detected. ARP and ping tests skipped.")
            return issue_found, "\n".join(full_report)

        # Step 2: ARP checks
        arp_passed, arp_report = self.run_arp_tests()
        full_report.append(arp_report)

        if not arp_passed:
            issue_found = True
            full_report.append("\n[INFO] ARP problems detected. Ping test skipped.")
            return issue_found, "\n".join(full_report)

        # Step 3: LAN ping
        ### to be added ###

        return not issue_found, "\n".join(full_report)
