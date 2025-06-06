import sys
import os
import django
import ipaddress
from datetime import timedelta
from django.utils.timezone import now

# Set up access to the Django environment by adding the project to PYTHONPATH
sys.path.append("/home/user/Projet-Python-TSP/DiagnosticTool")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DiagnosticTool.settings')
django.setup()

from core.models import ARP_CONF, ARP_TEST, Interface_TEST

def check_arp_test_has_data():
    """
    Check if ARP_TEST table has any entries
    """
    count = ARP_TEST.objects.count()
    if count == 0:
        print("[ERROR] No entries found in ARP_TEST table.")
        return False
    else:
        print(f"[INFO] {count} entries found in ARP_TEST table.")
        return True

def check_arp_ip_in_interface_network():
    """
    For each ARP_TEST entry, check if the IP is in the same network as its interface
    """
    errors = 0
    ten_minutes_ago = now() - timedelta(minutes=10)
    for entry in ARP_TEST.objects.filter(timestamp__gte=ten_minutes_ago):
        interface = entry.idinterface
        arp_ip = entry.ip_arp

        if not interface.ip_address or not interface.subnet_mask:
            print(f"[WARNING] Interface {interface.idinterface} has missing IP address or subnet mask.")
            continue

        try:
            interface_network = ipaddress.ip_interface(f"{interface.ip_address}/{interface.subnet_mask}").network
            arp_ip_obj = ipaddress.ip_address(arp_ip)
            if arp_ip_obj not in interface_network:
                print(f"[ERROR] ARP IP {arp_ip} is NOT in the network {interface_network} of interface {interface.idinterface}.")
                errors += 1
            else:
                print(f"[OK] ARP IP {arp_ip} is in the network {interface_network} of interface {interface.idinterface}.")
        except Exception as e:
            print(f"[ERROR] Failed to check ARP entry {arp_ip} for interface {interface.idinterface}: {e}")
            errors += 1

    if errors == 0:
        print("[INFO] All ARP IPs are in their respective networks.")
        return True
    else:
        print(f"[SUMMARY] {errors} errors found in ARP IPs network check.")
        return False

def compare_arp_conf_and_test():
    """
    Compare ARP_CONF and ARP_TEST tables, and print differences
    """
    differences = 0
    # check if ARP_CONF entries are in ARP_TEST
    for conf_entry in ARP_CONF.objects.all():
        ip_conf = conf_entry.ip_arp
        idinterface_conf = conf_entry.idinterface.idinterface  # receive the idinterface of the interface linked with ARP

        # Verify that the entry exists in ARP_TEST
        match = ARP_TEST.objects.filter(idinterface__idinterface=idinterface_conf,ip_arp=ip_conf).order_by('-timestamp').first()
        
        if not match:
            print(f"[DIFF] ARP_CONF entry {ip_conf} (interface {idinterface_conf}) NOT found in ARP_TEST.")
            differences += 1

    # check if there are ARP_TEST entries that are not in ARP_CONF
    for test_entry in ARP_TEST.objects.all():
        ip_test = test_entry.ip_arp
        idinterface_test = test_entry.idinterface.idinterface

        match = ARP_CONF.objects.filter(idinterface__idinterface=idinterface_test, ip_arp=ip_test).first()

        if not match:
            print(f"[INFO] ARP_TEST entry {ip_test} (interface {idinterface_test}) NOT found in ARP_CONF. (This may be normal for new entries)")

    if differences == 0:
        print("[INFO] All ARP_CONF entries are present in ARP_TEST.")
        
    else:
        print(f"[SUMMARY] {differences} ARP_CONF entries missing in ARP_TEST.")
        

def main():
    step1 = check_arp_test_has_data()
    if not step1:
        return False

    step2 = check_arp_ip_in_interface_network()
    compare_arp_conf_and_test()

    if step1 and step2:
        print("Success !")
        return True
    else:
        print("Some tests failed. Check logs.")
        return False

if __name__ == "__main__":
    main()
