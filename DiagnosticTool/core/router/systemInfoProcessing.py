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
from core.models import Router, security

def activated_protocol(status):
    """
    Indicates if the procol is activated or not
    """
    return "Up" if status == 1 else "Down"

def parse_sys_infos_from_json(data):
    """
    Parses system infos metrics json data.
    Extracts hostname, sys_descr, uptime, SNMP version, CDP, SSH and telnet statut
    [to be improved]
    Returns a list of structured system entries.
    """

    parsed_entries=[]
    
    fields = data.get("fields", {})

    parsed_entry = {
        "sysName": fields.get("sysName"),
        "sysDescr": fields.get("sysDescr"),
        "sysUptime": fields.get("sysUptime"),
        "cdp_status": fields.get("cdp_global_status")
    }

    parsed_entries.append(parsed_entry)

    return parsed_entries

if __name__ == "__main__":

    json_path = "/home/user/Projet-Python-TSP/DiagnosticTool/data/security_sample.json"
    with open(json_path, "r") as f:
        data = json.load(f)
    infos = parse_sys_infos_from_json(data)
    print(infos)