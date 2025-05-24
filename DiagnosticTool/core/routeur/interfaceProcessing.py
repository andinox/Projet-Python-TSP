#!/usr/bin/env python3

import traceback
import sys
import os
import django
from django.utils.timezone import now
from core.models import  Router, Interface_CONF, Interface_TEST, ARP_CONF

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
    # retrieving router information
    router = Router.objects.first()
    if not router:
        log_debug("[ERROR] No router found")
        return

    for entry in entries:
        try:
            interface_index = entry.get("idinterface")
            if interface_index is None:
                log_debug(f"[SKIP] No idinterface provided in entry: {entry}")
                continue

            # preparing common interface data
            interface_data = {
                "idinterface": interface_index,
                "router": router,
                "interface_name": entry.get("interface"),
                "admin_status": entry.get("admin"),
                "reachability": entry.get("reachability"),
                "ip_address": entry.get("interface_ip"),
                "timestamp": now()
            }

            interface_conf = Interface_CONF.objects.filter(idinterface=interface_index).first()

            if not interface_conf:
                # first time: create in Interface_CONF and Interface_TEST
                Interface_CONF.objects.create(**interface_data)
                Interface_TEST.objects.create(**interface_data)
                log_debug(f"[CREATE] Interface_CONF & Interface_TEST created for '{interface_data['interface_name']}' (id {interface_index}).")
            else:
                # get last recorded state from Interface_TEST
                last_test = Interface_TEST.objects.filter(idinterface=interface_index).order_by('-timestamp').first()

                # if no test entry exists yet (rare case)
                if not last_test:
                    Interface_TEST.objects.create(**interface_data)
                    log_debug(f"[HISTORY] No previous Interface_TEST found, created new for '{interface_data['interface_name']}' (id {interface_index}).")
                    continue

                # check for actual change
                changed = (
                    (last_test.admin_status or "").strip().lower() != (interface_data["admin_status"] or "").strip().lower() or
                    (last_test.reachability or "").strip().lower() != (interface_data["reachability"] or "").strip().lower() or
                    (last_test.ip_address or "").strip() != (interface_data["ip_address"] or "").strip()
                )

                if changed:
                    Interface_TEST.objects.create(**interface_data)
                    log_debug(f"[CHANGE] Interface_TEST created due to change from last TEST for '{interface_data['interface_name']}' (id {interface_index}).")
                else:
                    log_debug(f"[NO CHANGE] No changes detected compared to last Interface_TEST for '{interface_data['interface_name']}' (id {interface_index}).")

        except Exception as e:
            log_debug(f"[ERROR] Failed to process interface (id {entry.get('idinterface')}): {e}")
            log_debug(traceback.format_exc())
