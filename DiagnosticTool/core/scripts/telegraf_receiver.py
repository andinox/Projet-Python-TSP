#!/usr/bin/env python3

import sys
import json
import django
import os

# Set up access to the Django environment by adding the project to PYTHONPATH
# and specifying the settings module
sys.path.append("/home/user/Projet-Python-TSP/DiagnosticTool")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DiagnosticTool.settings')
django.setup()

# Importation of Router & Interface models (we will add later the other ones such as BGP, ARP etc.)
from core.models import Router, Interface
from django.utils.timezone import now

def status_to_text(val):
    return "up" if val==1 else "down"

def main():
    for line in sys.stdin:
        try:
            with open("/tmp/telegraf_exec_test.log", "a") as f:
                f.write("Script appelé par Telegraf\n")

            data = json.loads(line)

            with open("/tmp/telegraf_metrics.json", "a") as f:
                f.write(json.dumps(data) + "\n")
            print("Nouveau paquet Telegraf reçu :")
            print(json.dumps(data, indent=2))

            with open("/tmp/telegraf_metrics_clean.log","a") as log:
                # retrieving interface infos
                log.write("-- INTERFACES --\n")
                if "metrics" in data:
                    for m in data["metrics"]:
                        if m.get("name") == "interface_status":
                            f=m.get("fields", {})
                            interface=f.get("interface_name", "inconnu") # inconnu by default
                            admin=status_to_text(f.get("ifAdminStatus", -1)) # -1 by default
                            reachability=status_to_text(f.get("ifOperStatus", -1)) # -1 if not found (default)
                            log.write(f"Interface {interface}: admin={admin}, reachability={reachability}\n")

                            # Creation of an Interface with retrieved datas
                            try:
                                router_name = data.get("tags", {}).get("router")
                                router = Router.objects.get(name=router_name)

                                Interface.objects.create(
                                    router=router,
                                    interface_name=interface,
                                    admin_status=admin,
                                    reachability=reachability,
                                    ip_address=data.get("tags", {}).get("ip_address", "0.0.0.0"), # 0.0.0.0 by default
                                    timestamp=now()
                                )

                            except Router.DoesNotExist:
                                log.write(f"ERROR --  routeur {router_name} not found \n")
                            except Exception as e:
                                log.write(f"ERROR -- while saving an interface : {e}\n")

        except json.JSONDecodeError as e:
            print("Erreur de parsing JSON :", e)

if __name__ == "__main__":
    main()
