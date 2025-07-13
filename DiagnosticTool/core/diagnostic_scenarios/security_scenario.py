from core.models import  Security, SecurityScan, Diagnostic
from core.router import perform_security_scan
from core.scripts import convert_uptime
from dotenv import load_dotenv
import os

load_dotenv()

class SecurityDiagnostic:
    def __init__(self, diagnostic: Diagnostic):
        self.diagnostic = diagnostic
        self.router = diagnostic.router

    def run(self,skip_basic_network_tests=False):
        """
        :param skip_basic_network_tests: no needed here but for other class ; in scenarios.py it will be used as false to not get an issue with the loop
        Runs the security diagnostic using system info from DB and a live port scan.

        Returns:
        str: A diagnostic report including system info and open ports.
        """
        report = []
        report.append("\nDÉBUT DU DIAGNOSTIC : Je souhaite vérifier la sécurité de mon réseau\n\n")

        # Retrieve system info from DB
        security_obj = Security.objects.filter(hostname=self.router.name).order_by("-id").first()

        if not security_obj:
            report.append(f"[ERROR] No security entry found for router hostname: {self.router.name}")
            return "\n".join(report)

        readable_uptime = convert_uptime(security_obj.uptime)
        
        report.append(f"[INFO] Hostname: {security_obj.hostname}")
        report.append(f"[INFO] Description: {security_obj.sys_descr}")
        report.append(f"[INFO] Uptime: {readable_uptime}")
        report.append(f"[INFO] CDP Enabled: {'Yes' if security_obj.cdp_enabled else 'No'}\n")

        # Perform and sync port scan
        router_ip = os.getenv("ROUTER_IP") or self.router.management_ip
        if not router_ip:
            report.append("[ERROR] No router IP configured.")
            return "\n".join(report)

        perform_security_scan(router_ip, security_obj.hostname)

        # === 3. Fetch and display scan results ===
        report.append("\n")
        report.append("----- PORTS OUVERTS APRÈS SCAN NMAP -----")
        scans = SecurityScan.objects.filter(security=security_obj)

        if not scans.exists():
            report.append(f"[INFO] Pas de ports ouverts pour {router_ip}.")
        else:
            for scan in scans:
                line = f"\n{scan.protocol.upper()} port {scan.port}: {scan.service_name} ({scan.product or ''} {scan.version or ''})"
                report.append(line)
                if scan.extrainfo:
                    report.append(f"   [INFO] {scan.extrainfo}")
                report.append("----------------------------------------")

        return "\n".join(report)
