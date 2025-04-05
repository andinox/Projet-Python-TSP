#!/usr/bin/env python3

import sys
import json

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
                            interface=f.get("interface_name", "inconnu")
                            admin=status_to_text(f.get("ifAdminStatus", -1))
                            reachability=status_to_text(f.get("ifOperStatus", -1))
                            log.write(f"Interface {interface}: admin={admin}, reachability={reachability}\n")

        except json.JSONDecodeError as e:
            print("Erreur de parsing JSON :", e)

if __name__ == "__main__":
    main()
