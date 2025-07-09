#!/home/user/python-project/bin/python

import sys
import os
import json
import django
from dotenv import load_dotenv
import os

# Set up access to the Django environment by adding the project to PYTHONPATH
# and specifying the settings module
sys.path.append("/home/user/Projet-Python-TSP/DiagnosticTool")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DiagnosticTool.settings')
django.setup()

# functions importation
from core.router.interfaceProcessing import save_interfaces_to_db, parse_interface_from_json
from core.router.ARPProcessing import save_arp_entries_to_db, parse_arp_from_json
from core.router.BGPProcessing import save_bgp_entries, parse_bgp_from_json
from core.router.BGPProcessing import log_debug
from core.router.systemInfoProcessing import parse_sys_infos_from_json, save_security_entries, perform_security_scan

load_dotenv()

ROUTER_IP = os.getenv("ROUTER_IP")

def main():
    lines = list(sys.stdin)
    log_debug("Starting receiver")
    for line in lines:
        try:
            log_debug("--MAIN EXECUTED--")
            data = json.loads(line)

            arp_entries = parse_arp_from_json(data)
            interface_entries = parse_interface_from_json(data)
            bgp_entries = parse_bgp_from_json(data)
            security_entries=parse_sys_infos_from_json(data)

            save_interfaces_to_db(interface_entries)
            save_arp_entries_to_db(arp_entries)
            save_bgp_entries(bgp_entries)
            save_security_entries(security_entries)
            save_security_entries(security_entries)
            
            if security_entries:
                hostname = security_entries[0].get("sysName")
                log_debug(f"[SCAN] Lancement du scan de sécurité sur {ROUTER_IP} pour {hostname}")
                perform_security_scan(ROUTER_IP, hostname)
            else:
                log_debug("[SECU][WARN] Aucun hostname trouvé, scan de sécurité non effectué")

        except json.JSONDecodeError as e:
            log_debug(f"[ERREUR JSON] : {e}")
        except Exception as e:
            import traceback
            log_debug(f"[ERREUR] : {e}")
            traceback.print_exc()

if __name__ == "__main__":
    main()


