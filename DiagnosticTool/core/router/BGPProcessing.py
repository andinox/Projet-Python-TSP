#!/usr/bin/env python3
import json
import os
import sys
import traceback
import django

# Setup Django environment
sys.path.append("/home/user/Projet-Python-TSP/DiagnosticTool")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DiagnosticTool.settings")
django.setup()

from django.utils.timezone import now
from core.models import Router, BGP_CONF, BGP_TEST


def map_peer_status_to_updown(status):
    """
    Converts a numeric BGP peer status to a human-readable string.
    Returns "up" if the status is 6 which means the BGP session is "Established", otherwise returns "down".
    """
    return "Up" if status == 6 else "Down"


def log_debug(message):
    """
    Appends a debug message to the /tmp/debug_bgp.log file.
    """
    with open("/tmp/debug_bgp.log", "a") as f:
        f.write(message + "\n")


def parse_bgp_from_json(json_data):
    """
    Parses BGP-related metrics from the SNMP json data.
    Extracts peer IP, ASN, peer_status, last_change.
    Returns a list of structured BGP entries.
    """
    parsed_entries = []

    if "metrics" not in json_data:
        return parsed_entries

    for m in json_data["metrics"]:
        if m.get("name") == "bgp_peers":
            f = m.get("fields", {})
            tags = m.get("tags", {})

            parsed_entry = {
                "neighbor_ip": f.get("peer_ip"),
                "asn": f.get("peer_as"),
                "up_down_status": map_peer_status_to_updown(f.get("peer_status")),
                "time_last_change": f"{f.get('peer_last_change')} sec",
            }

            parsed_entries.append(parsed_entry)

    return parsed_entries

def save_bgp_entries(entries):
    """
    Saves BGP entries to the database.
    - If neighbor is new: insert into BGP_CONF and BGP_TEST
    - If already exists in CONF: insert into BGP_TEST only if data changed
    """

    router = Router.objects.first()
    if not router:
        log_debug("[ERREUR] Aucun routeur détecté.")
        return

    for entry in entries:
        try:
            neighbor_ip = (entry.get("neighbor_ip") or "").strip()
            asn = entry.get("asn")
            up_down_status = (entry.get("up_down_status") or "").strip()
            time_last_change = (entry.get("time_last_change") or "").strip()

            bgp_data = {
                "router": router,
                "neighbor_ip": neighbor_ip,
                "asn": asn,
                "up_down_status": up_down_status,
                "time_last_change": time_last_change,
                "timestamp": now(),
            }

            # check if IP is already in BGP_CONF
            log_debug(f"[DEBUG] neighbor_ip: {neighbor_ip}, asn: {asn}, up_down_status: {up_down_status}, time_last_change: {time_last_change}")
            conf_exists = BGP_CONF.objects.filter(neighbor_ip=neighbor_ip).exists()
            log_debug(f"[DEBUG] BGP_CONF existe pour {asn} - {neighbor_ip}: {conf_exists}")

            if not conf_exists:
                try:
                    BGP_CONF.objects.create(**bgp_data)
                    log_debug(f"[CONF] Création d'une entrée BGP_CONF pour {asn}")
                except Exception as e:
                    log_debug(f"[ERREUR] Échec de création d'une entrée BGP_CONF pour {asn}: {e}")
                    log_debug(traceback.format_exc())
                    continue 

                # also insert first TEST entry
                try:
                    BGP_TEST.objects.create(**bgp_data)
                    log_debug(f"[TEST] Entrée BGP_TEST créée pour {asn}")
                except Exception as e:
                    log_debug(f"[ERREUR] Échec de création de l'entrée initiale BGP_TEST {asn}: {e}")
                    log_debug(traceback.format_exc())

                continue

            # check if TEST entry needs update
            last_test = (
                BGP_TEST.objects.filter(neighbor_ip=neighbor_ip)
                .order_by("-timestamp")
                .first()
            )

            if not last_test:
                BGP_TEST.objects.create(**bgp_data)
                log_debug(f"[TEST] Première entrée BGP_TEST créee pour {neighbor_ip}")
                continue

            changed = (
                last_test.asn != asn
                or (last_test.up_down_status or "").strip().lower()
                   != up_down_status.lower()
                or (last_test.time_last_change or "").strip() != time_last_change
            )

            if changed:
                BGP_TEST.objects.create(**bgp_data)
                log_debug(f"[CHANGEMENT] Nouvelle entrée BGP_TEST créée pour {neighbor_ip}")
            else:
                log_debug(f"[INFO] Pas de mise à jour requise pour {neighbor_ip}")

        except Exception as e:
            log_debug(f"[ERREUR] Erreur inattendue pour {entry.get('neighbor_ip')}: {e}")
            log_debug(traceback.format_exc())

# For testing, we will delete after real BGP is OK
def main():
    try:
        data_file = "/home/user/Projet-Python-TSP/DiagnosticTool/data/bgp_sample.json"

        # Load JSON data from file
        with open(data_file, "r") as f:
            json_data = json.load(f)

        # Parse
        entries = parse_bgp_from_json(json_data)
        print(f"Entrées {len(entries)} parsées.")

        # Print parsed entries
        for i, entry in enumerate(entries, start=1):
            print(f"\n--- Entry {i} ---")
            for key, value in entry.items():
                print(f"{key}: {value}")

        save_bgp_entries(entries)
        print("Entrées BGP sauvegardées dans la base de données.")

    except Exception as e:
        log_debug(f"[Erreur] Exception dans main_insert_bgp.py: {e}")
        log_debug(traceback.format_exc())
        print(f"Erreur: {e}")


if __name__ == "__main__":
    main()
