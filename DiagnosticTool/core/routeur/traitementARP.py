#!/usr/bin/env python3

from core.models import Interface, ARP
from core.routeur.general_functions import log_debug

def parse_arp_from_json(json_data):
    parsed_entries = []

    if "metrics" not in json_data:
        return parsed_entries

    for metric in json_data["metrics"]:
        if metric.get("name") == "arp_table":
            tags = metric.get("tags", {})
            fields = metric.get("fields", {})
            parsed_entry = {
                "ip_arp": tags.get("ipNetToMediaNetAddress"),
                "idinterface": tags.get("ipNetToMediaIfIndex")
            }
            parsed_entries.append(parsed_entry)
    
    return parsed_entries

def save_arp_entries_to_db(arp_entries):
    log_debug(f"[DEBUG] Entries to save : {arp_entries}")
    for entry in arp_entries:
        try:
            interface = Interface.objects.get(idinterface=entry["idinterface"])
            if not interface:
                log_debug("[ERROR] No interface found in base.")
                continue 
            
            arp = ARP(
                ip_arp=entry["ip_arp"],
                idinterface=interface
            )
            arp.save()
            log_debug(f"[DEBUG] ARP saved with IP {entry['ip_arp']} for interface {entry['idinterface']}")

        except Exception as e:
            log_debug(f"[ERREUR] Insertion ARP : {e}")
