#!/usr/bin/env python3

import traceback

# Importation of Router, Interface_TEST and Interface_CONF models
from core.models import Router, Interface_CONF, Interface_TEST
from django.utils.timezone import now
from core.router import log_debug


def status_to_text(val):
    """
    Converts a numeric interface status to a human-readable string.
    Returns "up" if the status is 1, otherwise returns "down".
    """
    return "up" if val == 1 else "down"


def log_debug(message):
    """
    Appends a debug message to the /tmp/debug_interfaces.log file.
    """
    with open("/tmp/debug_interfaces.log", "a") as f:
        f.write(message + "\n")


def parse_interface_from_json(json_data):
    """
    Parses interface-related metrics from the SNMP json data.
    Extracts administrative status, operational status, IP address, and subnet mask
    for each network interface. Returns a list of structured interface entries.
    """
    parsed_entries = []

    if "metrics" not in json_data:
        return parsed_entries

    interface_ip_map = {}
    for m in json_data["metrics"]:
        if m.get("name") == "interface_ip":
            f = m.get("fields", {})
            interface_index = f.get("interface_index")
            ip_address = f.get("ip_address")
            subnet_mask = f.get("ipAdEntNetMask")
            if interface_index is not None:
                interface_ip_map[interface_index] = {
                    "ip": ip_address,
                    "subnet_mask": subnet_mask,
                }

    for m in json_data["metrics"]:
        if m.get("name") == "interface_status":
            f = m.get("fields", {})
            interface_index = f.get("interface_index")
            if interface_index is None:
                continue

            ip_info = interface_ip_map.get(interface_index, {})
            ip_address = ip_info.get("ip")
            subnet_mask = ip_info.get("subnet_mask")

            parsed_entry = {
                "idinterface": interface_index,
                "interface": f.get("interface_name") or f.get("ifDescr", "inconnu"),
                "admin": status_to_text(f.get("ifAdminStatus", -1)),
                "reachability": status_to_text(f.get("ifOperStatus", -1)),
                "interface_ip": ip_address,
                "subnet_mask": subnet_mask,
            }

            parsed_entries.append(parsed_entry)

    return parsed_entries


def save_interfaces_to_db(entries):
    """
    Saves interface entries to the database.
    - If the interface is new: adds it to Interface_CONF and Interface_TEST.
    - If the interface already exists: checks for changes compared to the last TEST record.
    If changes are detected (admin status, reachability, or IP), a new TEST record is created.
    """

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
                "subnet_mask": entry.get("subnet_mask"),
                "timestamp": now(),
            }

            interface_conf = Interface_CONF.objects.filter(
                idinterface=interface_index
            ).first()

            if not interface_conf:
                # first time: create in Interface_CONF and Interface_TEST
                Interface_CONF.objects.create(**interface_data)
                Interface_TEST.objects.create(**interface_data)
                log_debug(
                    f"[CREATE] Interface_CONF & Interface_TEST created for '{interface_data['interface_name']}' (id {interface_index})."
                )
            else:
                # get last recorded state from Interface_TEST
                last_test = (
                    Interface_TEST.objects.filter(idinterface=interface_index)
                    .order_by("-timestamp")
                    .first()
                )

                # if no test entry exists yet
                if not last_test:
                    Interface_TEST.objects.create(**interface_data)
                    log_debug(
                        f"[HISTORY] No previous Interface_TEST found, created new for '{interface_data['interface_name']}' (id {interface_index})."
                    )
                    continue

                # check for actual change
                changed = (
                    (last_test.admin_status or "").strip().lower()
                    != (interface_data["admin_status"] or "").strip().lower()
                    or (last_test.reachability or "").strip().lower()
                    != (interface_data["reachability"] or "").strip().lower()
                    or (last_test.ip_address or "").strip()
                    != (interface_data["ip_address"] or "").strip()
                )

                if changed:
                    Interface_TEST.objects.create(**interface_data)
                    log_debug(
                        f"[CHANGE] Interface_TEST created due to change from last TEST for '{interface_data['interface_name']}' (id {interface_index})."
                    )
                else:
                    log_debug(
                        f"[NO CHANGE] No changes detected compared to last Interface_TEST for '{interface_data['interface_name']}' (id {interface_index})."
                    )

        except Exception as e:
            log_debug(
                f"[ERROR] Failed to process interface (id {entry.get('idinterface')}): {e}"
            )
            log_debug(traceback.format_exc())
