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

    def run(self, skip_basic_network_tests=False):
        report = []
        report.append("DÉBUT DU DIAGNOSTIC : Je souhaite vérifier la sécurité de mon réseau\n")

        # 1. System info
        security_obj = Security.objects.filter(hostname=self.router.name).order_by("-id").first()
        if not security_obj:
            report.append(f"[ERREUR] Aucune entrée de sécurité trouvée pour : {self.router.name}")
            return "\n".join(report)

        readable_uptime = convert_uptime(security_obj.uptime)

        report.append("Informations Système :\n")
        report.append(f"- Hostname     : {security_obj.hostname}")

        # Clean multiline sys_descr
        report.append("- Description  :")
        for line in security_obj.sys_descr.strip().splitlines():
            report.append(f"    {line.strip()}")

        report.append(f"- Uptime       : {readable_uptime}")
        report.append(f"- CDP Activé   : {'Oui' if security_obj.cdp_enabled else 'Non'}")

        # Add CDP recommendation if enabled
        if security_obj.cdp_enabled:
            report.append("(!)  Recommandation : Le protocole CDP peut exposer des infos réseau. Désactivez-le si non nécessaire.")
        report.append("\n")
        report.append("-" * 60)

        # 2. Ports scan
        router_ip = os.getenv("ROUTER_IP") or self.router.management_ip
        if not router_ip:
            report.append("[ERREUR] Aucune IP de routeur définie.")
            return "\n".join(report)

        perform_security_scan(router_ip, security_obj.hostname)

        report.append("Résultats du scan de ports (Nmap) :")
        report.append("-" * 60)

        scans = SecurityScan.objects.filter(security=security_obj)

        if not scans.exists():
            report.append(f"[INFO] Aucun port ouvert détecté sur {router_ip}.")
            report.append("Recommandation : Gardez votre pare-feu actif et surveillez les accès réseau.")
        else:
            for scan in scans:
                port = scan.port
                service = scan.service_name.lower()
                protocol = scan.protocol.upper()

                report.append(f"{protocol} port {port}: {service} ({(scan.product or '').strip()} {(scan.version or '').strip()})".strip())

                if scan.extrainfo:
                    report.append(f"  Info complémentaire : {scan.extrainfo.strip()}")

                # Add recommendation
                recommendation = self._get_recommendation(port, service)
                if recommendation:
                    report.append(f"(!)  Recommandation : {recommendation}")


        report.append("Diagnostic terminé.")

        return "\n".join(report)


    def _get_recommendation(self, port, service):
        if service in ["telnet"] or port == 23:
            return "Telnet est peu sécurisé. Utilisez SSH à la place et désactivez ce service."
        elif service == "ftp" or port == 21:
            return "FTP est non chiffré. Préférez SFTP ou FTPS pour plus de sécurité."
        elif service == "ssh" or port == 22:
            return "Utilisez des clés SSH et désactivez l'authentification par mot de passe."
        elif service == "http" or port == 80:
            return "HTTP est non chiffré. Préférez HTTPS pour sécuriser les échanges."
        elif port == 443 or service in ["https"]:
            return "Assurez-vous que le certificat TLS est valide et à jour."
        elif service == "snmp" or port == 161:
            return "Vérifiez les versions SNMP utilisées (préférez v3) et sécurisez les communautés."
        elif port == 3389:
            return "RDP détecté. Restreignez les accès et activez la sécurité réseau (NLA)."
        elif port == 3306:
            return "MySQL ouvert. Limitez l'accès à ce port et utilisez un mot de passe fort."
        elif port == 8080:
            return "Port HTTP alternatif. Appliquez les mêmes précautions que pour le port 80."
        else:
            return None

