#!/usr/bin/env python3
import json
import os
import sys
import traceback
import django
import logging

# Setup Django environment
sys.path.append("/home/user/Projet-Python-TSP/DiagnosticTool")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DiagnosticTool.settings")
django.setup()

from django.utils.timezone import now
from core.models import Router, Security
from core.router.general_functions import log_debug

def activated_protocol(status):
    """
    Indicates if the procol is activated or not
    """
    return "Up" if status == 1 else "Down"

def parse_sys_infos_from_json(data):
    log_debug(f"[SECU] Script lancé avec data: {data}")

    parsed_entries = []

    for metric in data.get("metrics", []):
        
        fields = metric.get("fields", {})
        parsed = {
            "sysName": fields.get("sysName"),
            "sysDescr": fields.get("sysDescr"),
            "sysUptime": fields.get("sysUptime"),
            "cdp_status": fields.get("cdp_global_status")
        }
        log_debug(f"[SECU] Champs extraits : {parsed}")
        parsed_entries.append(parsed)

    return parsed_entries




def save_security_entries(parsed_entries):
    """
    Saves a list of parsed system entries into the Security model.
    Only creates or updates records if data has changed.
    """
    for entry in parsed_entries:
        hostname = entry.get("sysName")
        sys_descr = entry.get("sysDescr")
        uptime = entry.get("sysUptime")
        cdp_status = entry.get("cdp_status")
        cdp_enabled = True if cdp_status == 1 else False

        
        #if not hostname:
        #    log_debug(f"[SECU] Entrée ignorée : hostname manquant dans {entry}")
        #    continue

        existing = Security.objects.filter(hostname=hostname).first()

        if existing:
            if (
                existing.sys_descr != sys_descr or
                existing.uptime != uptime or
                existing.cdp_enabled != cdp_enabled
            ):
                existing.sys_descr = sys_descr
                existing.uptime = uptime
                existing.cdp_enabled = cdp_enabled
                existing.save()
                log_debug(f"[SECU] ENTRÉE MODIFIÉE POUR L'HÔTE : {hostname}")
            else:
                log_debug(f"[SECU] Pas de changement détecté pour l'hôte: {hostname}")
        else:
            Security.objects.create(
                hostname=hostname,
                sys_descr=sys_descr,
                uptime=uptime,
                cdp_enabled=cdp_enabled
            )
            log_debug(f"[SECU] Nouvelle entrée de sécurité crée pour l'hôte : {hostname}")