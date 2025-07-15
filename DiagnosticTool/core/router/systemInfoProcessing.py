#!/home/user/python-project/bin/python
import os
import sys
import django
import nmap
from datetime import datetime

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

def perform_security_scan(ip: str, hostname: str, simulate=False):
    """
    Performs a Nmap scan and bulk updates the SecurityScan entries.
    """
    # Get latest Security entry for this hostname
    try:
        security_obj = Security.objects.filter(hostname=hostname).latest("id")
    except Security.DoesNotExist:
        return

    # Existing scans for this security object
    existing_scans = {
        (s.port, s.protocol): s
        for s in SecurityScan.objects.filter(security=security_obj)
    }

    # Scan results
    nm = nmap.PortScanner()
    nm.scan(hosts=ip, arguments='-sV')
    scan_results = []

    for proto in nm[ip].all_protocols():
        for port in nm[ip][proto].keys():
            result = nm[ip][proto][port]
            scan_results.append({
                "port": port,
                "protocol": proto,
                "service_name": result.get("name", ""),
                "product": result.get("product", ""),
                "version": result.get("version", ""),
                "extrainfo": result.get("extrainfo", ""),
            })

    now = datetime.now()
    to_update = []
    to_create = []

    # Compare results and decide if create/update is needed
    for entry in scan_results:
        key = (entry["port"], entry["protocol"])
        existing = existing_scans.get(key)

        if existing:
            
            if (
                existing.service_name != entry["service_name"]
                or existing.product != entry["product"]
                or existing.version != entry["version"]
                or existing.extrainfo != entry["extrainfo"]
            ):
                existing.service_name = entry["service_name"]
                existing.product = entry["product"]
                existing.version = entry["version"]
                existing.extrainfo = entry["extrainfo"]
                existing.timestamp = now
                to_update.append(existing)
        else:
            to_create.append(SecurityScan(
                security=security_obj,
                port=entry["port"],
                protocol=entry["protocol"],
                service_name=entry["service_name"],
                product=entry["product"],
                version=entry["version"],
                extrainfo=entry["extrainfo"],
                timestamp=now,
            ))

    # Execute bulk DB operations
    if to_update:
        SecurityScan.objects.bulk_update(to_update, ["service_name", "product", "version", "extrainfo", "timestamp"])
    if to_create:
        SecurityScan.objects.bulk_create(to_create)