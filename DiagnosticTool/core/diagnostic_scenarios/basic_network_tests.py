# basic_network_tests.py

from core.models import Interface_CONF, Interface_TEST, ARP_CONF
from django.utils.timezone import now
from core.scripts.LANStatus import check_arp_test_has_data,check_arp_ip_in_interface_network,compare_arp_conf_and_test
from core.scripts.basic_functions import ping

class BasicNetworkTests:
    def __init__(self, router=None):
        self.router = router

    def check_interface_status_from_tests(self, tests):
        """
        Check status from a list of Interface_TEST objects (already loaded).
        Returns:
            True if operationally up,
            False if reachability down and admin up,
            timedelta if admin down,
            None if no data.
        """
        if not tests:
            return None

        # Get latest test entry
        latest_test = max(tests, key=lambda x: x.timestamp, default=None)

        if not latest_test:
            return None

        reachability = (latest_test.reachability or "").strip().lower()
        if reachability == "up":
            return True

        admin_status = (latest_test.admin_status or "").strip().lower()
        if admin_status == "down":
            # Walk back in time for continuous admin down entries
            down_since = latest_test.timestamp
            for test in sorted(tests, key=lambda x: x.timestamp, reverse=True):
                if (test.admin_status or "").strip().lower() != "down":
                    break
                down_since = test.timestamp
            return now() - down_since

        # Admin is up but not reachable → link issue
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
        Returns:
            all_passed (bool): False if any problem was detected during the tests.
            report_lines (str): Full report of the ARP tests.
        """
        report_lines = ["\n[ARP] Lancement des vérifications ARP...\n"]
        all_passed = True

        # step 1 : Check if current ARP table has data
        status, message = check_arp_test_has_data()
        report_lines.append(message)
        if not status:
            all_passed = False

        # step 2 : Check if IPs from the ARP table are in the same network as the router interface they are linked with
        status, messages = check_arp_ip_in_interface_network()
        report_lines.extend(messages)
        if not status:
            all_passed = False

        # step 3 : compares if initial ARP table and current one have differences
        messages = compare_arp_conf_and_test()
        report_lines.extend(messages)

        return all_passed, "\n".join(report_lines)

    def report_interfaces_status(self):
        """
        Generate a report of the status of all interfaces.
        """
        interfaces = Interface_CONF.objects.prefetch_related("tests").all()
        issues_found = False
        report_lines = []

        for entry in interfaces:
            idinterface = entry.idinterface
            interface_name = entry.interface_name

            tests = list(entry.tests.all())  # saved in memory so we only do the query once

            if not tests:
                continue

            latest_test = max(tests, key=lambda x: x.timestamp, default=None)

            if not latest_test:
                continue

            admin_status = (latest_test.admin_status or "").strip().lower()
            reachability = (latest_test.reachability or "").strip().lower()

            result = self.check_interface_status_from_tests(tests)

            if result is not True:
                issues_found = True
                report_lines.append(f"\nInterface : {interface_name} ({idinterface})")
                report_lines.append(f"Admin status : {admin_status}")
                report_lines.append(f"Reachability : {reachability}")

                if result is False:
                    report_lines.append("Status : down")
                    report_lines.append("Diagnostic : L'interface est DOWN mais est admin UP → Il peut s'agir d'un problème de lien.")
                elif result is None:
                    report_lines.append("Status : Unknown")
                    report_lines.append("Diagnostic: Aucune donnée de test ou impossibilité de déterminer depuis quand l'interface est admin down.")
                else:
                    formatted = self.format_timedelta(result)
                    report_lines.append("Status : admin down")
                    report_lines.append(f"Diagnostic : l'interface est admin down depuis {formatted}")
            else:
                report_lines.append(f"\n[OK] Interface : {interface_name} ({idinterface})")
                report_lines.append(f"Admin status : {admin_status}")
                report_lines.append(f"Reachability : {reachability}")

        if not issues_found:
            report_lines.append("[OK] Tests sur les interfaces effectués avec succès, aucun problème à signaler.")

        return issues_found, "\n".join(report_lines)


    
    def run_all_basic_tests(self):
        """
        Run the full sequence of basic network tests:
        - interface status check
        - ARP table validation
        - LAN ping test

        Returns:
            issue_found (bool): True if any problem was detected during the tests.
            report (str): Full diagnostic report.
        """
        full_report = []
        issue_found = False

        full_report.append("[Tests Réseaux de base]")

        # Step 0: Preload all interface configurations to avoid duplicate SQL queries
        interface_conf_map = {
            interface.idinterface: interface
            for interface in Interface_CONF.objects.select_related("router")
        }

        # Step 1: Interface status check
        full_report.append("[INTERFACES] Lancement des tests sur les interfaces")
        interfaces_issue, interface_report = self.report_interfaces_status()
        full_report.append(interface_report)

        if interfaces_issue:
            issue_found = True
            full_report.append("\n[INFO] Problèmes d'interfaces détectés. Tests ARP et ping ignorés.")
            return issue_found, "\n".join(full_report)

        # Step 2: ARP tests
        full_report.append("\n[ARP] Lancement des vérifications ARP...\n")

        status, message = check_arp_test_has_data()
        full_report.append(message)
        if not status:
            issue_found = True
            return issue_found, "\n".join(full_report)

        status, messages = check_arp_ip_in_interface_network()
        full_report.extend(messages)
        if not status:
            issue_found = True
            return issue_found, "\n".join(full_report)

        # Compare ARP_CONF and ARP_TEST
        arp_compare_messages = compare_arp_conf_and_test(interface_conf_map )
        full_report.extend(arp_compare_messages)

        # Step 3: Ping test to one ARP IP in LAN
        arp_entry = ARP_CONF.objects.filter(idinterface=1).exclude(ip_arp="172.16.10.51").only("ip_arp").first()

        if arp_entry:
            ip = arp_entry.ip_arp
            if ping(ip):
                full_report.append(f"[OK] Les ping vers l'IP {ip} située dans le LAN ont réussi")
            else:
                issue_found = True
                full_report.append(f"[ECHEC] Impossible de faire de ping vers l'IP {ip} située dans le LAN")

        return issue_found, "\n".join(full_report)