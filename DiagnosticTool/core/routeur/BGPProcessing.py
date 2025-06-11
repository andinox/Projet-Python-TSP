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

    except Exception as e:
        log_debug(f"[Erreur] Exception dans main_insert_bgp.py: {e}")
        log_debug(traceback.format_exc())
        print(f"Erreur: {e}")

if __name__ == "__main__":
    main()
    
