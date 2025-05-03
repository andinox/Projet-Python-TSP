#!/usr/bin/env python3

import traceback
import sys
import os
import django
from django.utils.timezone import now
from core.models import Interface_CONF, Router, ARP_CONF

# Importation of Router & Interface_CONF models
from core.models import Router, Interface_CONF
from django.utils.timezone import now
from core.routeur.general_functions import log_debug

def status_to_text(val):
    return "up" if val==1 else "down"

def log_debug(message):
    with open('/tmp/debug_interfaces.log', 'a') as f:
        f.write(message + "\n")
        
# PARSING - INTERFACES
def parse_interface_from_json(json_data):
    parsed_entries = []

    if "metrics" not in json_data:
        return parsed_entries

    interface_ip_map = {}
    for m in json_data["metrics"]:
        if m.get("name") == "interface_ip":
            f = m.get("fields", {})
            interface_index = f.get("interface_index")
            ip_address = f.get("ip_address")
            if interface_index is not None:
                interface_ip_map[interface_index] = ip_address

    for m in json_data["metrics"]:
        if m.get("name") == "interface_status":
            f = m.get("fields", {})
            interface_index = f.get("interface_index")
            if interface_index is None:
                continue

            ip_address = interface_ip_map.get(interface_index, "0.0.0.0")

            parsed_entry = {
                "idinterface": interface_index,
                "interface": f.get("interface_name") or f.get("ifDescr", "inconnu"),
                "admin": status_to_text(f.get("ifAdminStatus", -1)),
                "reachability": status_to_text(f.get("ifOperStatus", -1)),
                "interface_ip": ip_address
            }

            parsed_entries.append(parsed_entry)

    return parsed_entries

  
# SAVE INTERFACES
def save_interfaces_to_db(entries):
    log_debug(f"[DEBUG] Entries to save : {entries}")

    router = Router.objects.first()
    if not router:
        log_debug("[ERROR] No router found")
        return

    for entry in entries:
        try:
            interface_index = entry.get("idinterface")
            if interface_index is None:
                log_debug(f"[SKIP] No idinterface (interface_index) provided in entry: {entry}")
                continue

            # retrieving parsed entries
            defaults = {
                "interface_name": entry.get("interface"),
                "admin_status": entry.get("admin"),
                "reachability": entry.get("reachability"),
                "ip_address": entry.get("interface_ip"),
                "router": router,
            }

            try:
                interface = Interface_CONF.objects.get(idinterface=interface_index)
                updated = False

                # comparing fields between entries (last and new one) - except timestamp - if there is a change : the interface is updated
                for field, value in defaults.items():
                    if getattr(interface, field) != value:
                        setattr(interface, field, value)
                        updated = True

                if updated:
                    interface.timestamp = now()
                    interface.save()
                    log_debug(f"[UPDATE] Interface '{interface.interface_name}' updated (id {interface.idinterface}).")
                else:
                    log_debug(f"[SKIP] Interface '{interface.interface_name}' (id {interface.idinterface}) not changed.")

            except Interface_CONF.DoesNotExist:

                Interface_CONF.objects.update_or_create(
                    idinterface=interface_index,
                    defaults={**defaults, "timestamp": now()}
                )
                log_debug(f"[CREATE] Interface '{defaults['interface_name']}' created (id {interface_index}).")

        except Exception as e:
            log_debug(f"[ERROR] Failed to process interface (id {entry.get('idinterface')}): {e}")
            log_debug(traceback.format_exc())