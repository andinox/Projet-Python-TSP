#!/usr/bin/env python3

import sys
import os
import django
from django.utils.timezone import now

# Setup Django environment
sys.path.append("/home/user/Projet-Python-TSP/DiagnosticTool")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DiagnosticTool.settings')
django.setup()

from core.models import Interface_CONF, Interface_TEST

def check_interface_status(idinterface):
    """
    Check the operational status of an interface.
    returns true if it is operationally up (reachable),
    returns timedelta if admin down (duration since down),
    returns false if link down,
    returns none if no test data.
    """
    
    #retrieve the latest test entry for the given interface
    latest_test = Interface_TEST.objects.filter(idinterface=idinterface).order_by('-timestamp').first()

    if not latest_test:
        return None

    #reachability and admin status checks
    reachability = (latest_test.reachability or "").strip().lower()
    if reachability == "up":
        return True

    admin_status = (latest_test.admin_status or "").strip().lower()
    if admin_status == "down":
        down_entries = Interface_TEST.objects.filter(
            idinterface=idinterface,
            admin_status__iexact='down'
        ).order_by('timestamp')

        if down_entries.exists():
            down_since = down_entries.first().timestamp
            return now() - down_since

        else:
            return None

    return False

def format_timedelta(delta):
    """Format is 'X days HH:MM:SS'"""
    total_seconds = int(delta.total_seconds())
    days = delta.days
    hours = (total_seconds % 86400) // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{days} days {hours:02}:{minutes:02}:{seconds:02}"

def report_interface_status():
    interfaces = Interface_CONF.objects.all()

    print("\n=== Interface operational status report ===")
    for entry in interfaces:
        idinterface = entry.idinterface
        interface_name = entry.interface_name

        latest_test = Interface_TEST.objects.filter(idinterface=idinterface).order_by('-timestamp').first()
        if not latest_test:
            print(f"\n{interface_name} ({idinterface}): No test data available.")
            continue

        admin_status = (latest_test.admin_status or "").strip().lower()
        reachability = (latest_test.reachability or "").strip().lower()

        result = check_interface_status(idinterface)

        print(f"\nInterface : {interface_name} ({idinterface})")
        print(f"Admin status : {admin_status}")
        print(f"Reachability : {reachability}")

        if result is True:
            print("Status : up")
        elif result is False:
            print("Status : down")
            print("Diagnostic : Interface is down but admin is up → It may be a possible link issue.")
        elif result is None:
            print("Status : Unknown")
            print("Diagnostic : No test data or cannot determine admin down time.")
        else:
            formatted = format_timedelta(result)
            print("Status : admin down")
            print(f"Diagnostic : admin down for {formatted}")

if __name__ == "__main__":
    report_interface_status()
