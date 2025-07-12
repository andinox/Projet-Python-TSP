#!/home/user/python-project/bin/python
import os
import sys
import django
import nmap

# Setup Django environment
sys.path.append("/home/user/Projet-Python-TSP/DiagnosticTool") # TODO: need to change the path or put it in variable maybe
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DiagnosticTool.settings")
django.setup()

from core.models import Security,SecurityScan
from core.router import log_debug

def activated_protocol(status):
    """
    Indicates if the procol is activated or not
    """
    return "Up" if status == 1 else "Down"

def parse_sys_infos_from_json(data):
    """
    Parses SNMP-related system info (sysName, sysDescr, sysUptime, CDP status) from Telegraf JSON input.
    Returns a list of dictionaries with extracted values.
    """
    log_debug(f"[SECU] Script lancé avec data: {data}")

    parsed_entries = []

    for metric in data.get("metrics", []):

        if metric.get("name")!="snmp":
            continue

        fields = metric.get("fields", {})
        parsed = {
            "sysName": fields.get("sysName"),
            "sysDescr": fields.get("sysDescr"),
            "sysUptime": fields.get("sysUptime"),
            "cdp_status": fields.get("cdp_global_status")
        }

        parsed_entries.append(parsed)

    return parsed_entries

def save_security_entries(parsed_entries):
    """
    Saves a list of parsed system entries into the Security model.
    Only creates or updates records if data has changed.
    """
    for entry in parsed_entries:
        hostname = entry.get("sysName")
        sys_descr = entry.get("sysDescr")
        uptime = entry.get("sysUptime")
        cdp_status = entry.get("cdp_status")
        cdp_enabled = True if cdp_status == 1 else False

        existing = Security.objects.filter(hostname=hostname).first()

        if existing:
            if (
                existing.sys_descr != sys_descr or
                existing.uptime != uptime or
                existing.cdp_enabled != cdp_enabled
            ):
                existing.sys_descr = sys_descr
                existing.uptime = uptime
                existing.cdp_enabled = cdp_enabled
                existing.save()
                log_debug(f"[SECU] ENTRÉE MODIFIÉE POUR L'HÔTE : {hostname}")
            else:
                log_debug(f"[SECU] Pas de changement détecté pour l'hôte: {hostname}")
        else:
            Security.objects.create(
                hostname=hostname,
                sys_descr=sys_descr,
                uptime=uptime,
                cdp_enabled=cdp_enabled
            )
            log_debug(f"[SECU] Nouvelle entrée de sécurité crée pour l'hôte : {hostname}")

def perform_security_scan(ip, hostname):
    """
    IP scan with Nmap and sync SecurityScan model
    """
    log_debug(f"[SECU][SCAN] Démarrage du scan Nmap sur {ip} pour {hostname}")

    try:
        nm = nmap.PortScanner()
        nm.scan(ip, arguments='-sV')
        log_debug(f"[SECU][SCAN] Hôtes détectés : {nm.all_hosts()}")

        if ip not in nm.all_hosts():
            log_debug(f"[SECU][SCAN] L'IP {ip} n'a pas été détectée par Nmap.")
            return

        security_obj = Security.objects.filter(hostname=hostname).first()
        if not security_obj:
            log_debug(f"[SECU][DB] Aucun objet Security trouvé pour hostname={hostname}")
            return

        # see active ports
        current_ports = set()

        for proto in nm[ip].all_protocols():
            log_debug(f"[SECU][SCAN] Protocole détecté : {proto}")
            for port in nm[ip][proto]:
                data = nm[ip][proto][port]
                log_debug(f"[SECU][SCAN] Port {port}/{proto} - data : {data}")

                current_ports.add((proto, port))

                SecurityScan.objects.update_or_create(
                    security=security_obj,
                    protocol=proto,
                    port=port,
                    defaults={
                        'service_name': data.get('name'),
                        'product': data.get('product'),
                        'version': data.get('version'),
                        'extrainfo': data.get('extrainfo'),
                    }
                )
                log_debug(f"[SECU][DB] Insertion/màj : {hostname} - {proto}/{port}")

        # removing ports that are closed
        saved_ports = SecurityScan.objects.filter(security=security_obj)
        for scan in saved_ports:
            if (scan.protocol, scan.port) not in current_ports:
                log_debug(f"[SECU][DB] Suppression de l'entrée obsolète : {scan.protocol}/{scan.port}")
                scan.delete()

    except Exception as e:
        import traceback
        log_debug(f"[SECU][ERROR] Exception lors du scan Nmap : {e}")
        traceback.print_exc()