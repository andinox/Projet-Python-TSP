# basic_network_tests.py

from core.models import Interface_CONF, ARP_CONF, ARP_TEST
from django.utils.timezone import now
from core.scripts import ping
import ipaddress
from datetime import timedelta
from django.utils.timezone import now
from django.db.models.functions import Random

class BasicNetworkTests:
    def __init__(self, router=None):
        self.router = router

    def check_arp_test_has_data(self):
        one_minute_ago = now() - timedelta(minutes=1)
        count = ARP_TEST.objects.filter(timestamp__gte=one_minute_ago).count()
        if count == 0:
            return False, "[ECHEC] Aucun enregistrement trouvé dans la table ARP. \n [Ticket] Erreur détectée côté LAN."
        else:
            return True, f"[OK] {count} enregistrements trouvés dans la table ARP récente."

    def check_arp_ip_in_interface_network(self):
        messages = []
        errors = 0
        one_minute_ago = now() - timedelta(minutes=1)

        entries = ARP_TEST.objects.select_related("idinterface").filter(timestamp__gte=one_minute_ago)

        if not entries.exists():
            messages.append("[ATTENTION] Aucun enregistrement ARP récent (moins de 1 minute) trouvé.")
            return False, messages

        for entry in entries:
            interface = entry.idinterface
            arp_ip = entry.ip_arp
            ip_addr = interface.ip_address
            mask = interface.subnet_mask

            if not ip_addr or not mask:
                messages.append(f"[AVERTISSEMENT] Interface {interface.idinterface} sans IP ou masque.")
                errors += 1
                continue

            try:
                network = ipaddress.ip_interface(f"{ip_addr}/{mask}").network
                arp_ip_obj = ipaddress.ip_address(arp_ip)

                if arp_ip_obj not in network:
                    messages.append(f"[ERREUR] ARP IP {arp_ip} hors du réseau {network} (interface {interface.idinterface}).")
                    errors += 1
                else:
                    messages.append(f"[OK] ARP IP {arp_ip} dans le réseau {network} (interface {interface.idinterface}).")
            except Exception as e:
                messages.append(f"[ERREUR] Vérification impossible pour {arp_ip} (interface {interface.idinterface}) : {e}")
                errors += 1

        if errors == 0:
            messages.append("[INFO] Tous les ARP IP sont dans leur réseau respectif.")
            return True, messages
        else:
            messages.append(f"[ECHEC] {errors} erreurs détectées lors de la vérification des IP ARP.")
            messages.append("[Ticket] Erreur détectée côté LAN.")
            return False, messages

    def compare_arp_conf_and_test(self, interface_conf_map):
        differences = 0
        messages = ["Comparaison entre la table ARP initiale et les entrées ARP_TEST récentes :"]
        one_minute_ago = now() - timedelta(minutes=1)

        arp_test_entries = ARP_TEST.objects.select_related("idinterface").filter(timestamp__gte=one_minute_ago)
        arp_conf_entries = ARP_CONF.objects.select_related("idinterface").all()

        conf_keys = {(entry.idinterface.idinterface, entry.ip_arp) for entry in arp_conf_entries}
        test_keys = {(entry.idinterface.idinterface.idinterface, entry.ip_arp) for entry in arp_test_entries}

        for key in conf_keys - test_keys:
            idinterface, ip = key
            interface = interface_conf_map.get(idinterface)
            name = interface.interface_name if interface else f"ID {idinterface}"
            messages.append(f"[DIFF] ARP_CONF {ip} (interface {name}) non trouvé dans ARP_TEST (récente).")
            differences += 1

        for key in test_keys - conf_keys:
            idinterface, ip = key
            interface = interface_conf_map.get(idinterface)
            name = interface.interface_name if interface else f"ID {idinterface}"
            messages.append(f"[INFO] ARP_TEST {ip} (interface {name}) non trouvé dans ARP_CONF (peut être normal).")

        if differences == 0:
            messages.append("[INFO] Toutes les IP ARP initiales sont présentes dans les données ARP récentes.")
        else:
            messages.append(f"[RÉSUMÉ] {differences} IP manquantes dans ARP_TEST récent comparé à ARP_CONF.")

        return messages

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
    
    def run_arp_tests(self,interface_conf_map):
        """
        Executes the three ARP checks and returns whether the tests were successful
         as well as the messages associated with the tests
        Returns:
            all_passed (bool): False if any problem was detected during the tests.
            report_lines (str): Full report of the ARP tests.
        """
        report_lines = ["\n"]
        all_passed = True

        # step 1 : Check if current ARP table has data
        status, message = self.check_arp_test_has_data()
        report_lines.append(message)
        if not status:
            all_passed = False

        # step 2 : Check if IPs from the ARP table are in the same network as the router interface they are linked with
        status, messages = self.check_arp_ip_in_interface_network()
        report_lines.extend(messages)
        if not status:
            all_passed = False

        # step 3 : compares if initial ARP table and current one have differences
        messages = self.compare_arp_conf_and_test(interface_conf_map)
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

        arp_ok, arp_report = self.run_arp_tests(interface_conf_map)
        full_report.append(arp_report)
        if not arp_ok:
            issue_found = True
            return issue_found, "\n".join(full_report)

        # Step 3: Ping test to one ARP IP in LAN
        arp_entry = ARP_CONF.objects.filter(idinterface=1).exclude(ip_arp="172.16.10.51").only("ip_arp").order_by(Random()).first()

        if arp_entry:
            ip = arp_entry.ip_arp
            if ping(ip):
                full_report.append(f"[OK] Les ping vers l'IP {ip} située dans le LAN ont réussi")
            else:
                issue_found = True
                full_report.append(f"[ECHEC] Impossible de faire de ping vers l'IP {ip} située dans le LAN")

        return issue_found, "\n".join(full_report)