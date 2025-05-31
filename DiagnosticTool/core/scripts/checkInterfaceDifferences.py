#!/usr/bin/env python3

import sys
import os
import django

# Setup Django environment
sys.path.append("/home/user/Projet-Python-TSP/DiagnosticTool")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DiagnosticTool.settings')
django.setup()

from core.models import Interface_CONF, Interface_TEST

def interface_status_comparison():
    """
    Verify that each entry in Interface_CONF matches the latest info in Interface_TEST
    returns True if all entries match, otherwise returns False.
    """
    
    for conf_entry in Interface_CONF.objects.all():
        idinterface=conf_entry.idinterface

        latest_test=Interface_TEST.objects.filter(idinterface=idinterface).order_by('-timestamp').first()

        # If no latest test entry found
        if not latest_test:
            print(f"No Interface_TEST found for idinterface {idinterface}")
            return False

        # Compare fields between conf entry and the latest test entry and collect differences; putting them in a list called "diffs"
        diffs = []
        
        if (conf_entry.admin_status or "").strip().lower() != (latest_test.admin_status or "").strip().lower():
            diffs.append("admin_status")
            
        if (conf_entry.reachability or "").strip().lower() != (latest_test.reachability or "").strip().lower():
            diffs.append("reachability")
            
        if (conf_entry.ip_address or "").strip() != (latest_test.ip_address or "").strip():
            diffs.append("ip_address")
            
        if (conf_entry.subnet_mask or "").strip() != (latest_test.subnet_mask or "").strip():
            diffs.append("subnet_mask")

        if diffs:
            print(f"Interface {conf_entry.interface_name} (id={idinterface}) has mismatches: {', '.join(diffs)}")
            return False

    print("Test is a success! All Interface_CONF entries match the latest Interface_TEST entries.")
    return True

def main():
    return interface_status_comparison()

if __name__ == "__main__":
    main()