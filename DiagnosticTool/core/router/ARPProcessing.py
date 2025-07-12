
import traceback
from django.utils.timezone import now
from core.models import Interface_CONF, Interface_TEST, ARP_CONF, ARP_TEST
from core.router.general_functions import log_debug
from datetime import timedelta
import ipaddress #necessary to calculate IP networks

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
            # --- ARP CONF ---
            try:
                interface = Interface_CONF.objects.get(idinterface=entry["idinterface"])
            except Interface_CONF.DoesNotExist:
                log_debug(f"[ERROR] Interface_CONF with idinterface={entry['idinterface']} not found.")
                continue

            ip_arp = entry["ip_arp"]
            if not ip_arp:
                log_debug("[SKIP] Missing ARP IP, skipping entry.")
                continue

            # verify if the IP is in the same network as the interface's IP
            try:
                interface_ip = ipaddress.ip_interface(f"{interface.ip_address}/{interface.subnet_mask}") #creating a network object to compare with the ARP IP
                arp_ip = ipaddress.ip_address(ip_arp) #creating a network object to verify if it's in the good network
                in_same_network = arp_ip in interface_ip.network
                log_debug(f"[DEBUG] Checking network: ARP {arp_ip} in {interface_ip.network} => {in_same_network}")
            except Exception as e:
                log_debug(f"[ERROR] Network check failed for interface {interface.idinterface}: {e}")
                in_same_network = False

            # if the IP is in the same network and the entry doesn't exist in ARP_CONF then we add it
            if in_same_network:
                existing_arp = ARP_CONF.objects.filter(ip_arp=ip_arp, idinterface=interface).first()
                if existing_arp:
                    log_debug(f"[SKIP] ARP entry already exists for IP {ip_arp} and interface {interface.idinterface}.")
                else:
                    newarp = ARP_CONF(
                        ip_arp=ip_arp,
                        idinterface=interface,
                        timestamp=now()
                    )
                    newarp.save()
                    log_debug(f"[CREATE] ARP entry saved for IP {ip_arp} on interface {interface.idinterface}.")
            else:
                log_debug(f"[SKIP] ARP IP {ip_arp} not in same network as interface {interface.idinterface}.")

            # --- ARP TEST ---
            interfaceT = Interface_TEST.objects.filter(idinterface=entry["idinterface"]).last()
            if not interfaceT:
                log_debug("[ERROR] No interface TEST found in base.")
                continue

            # cleaning old entries in ARP_TEST
            one_hour_ago = now() - timedelta(hours=1)
            deleted_count, _ = ARP_TEST.objects.filter(timestamp__lt=one_hour_ago).delete()
            if deleted_count > 0:
                log_debug(f"[CLEANUP] Deleted {deleted_count} ARP_TEST entries older than 1 hour.")

            # then we insert the entry in ARP_TEST, we don't verify if it already exists as it would not show the IPs that disapeared
            ARP_TEST.objects.create(
                ip_arp=ip_arp,
                idinterface=interfaceT,
                timestamp=now()
            )
            log_debug(f"[HISTORY] ARP_TEST saved for IP {ip_arp} (interface {interfaceT.idinterface}).")
        except Exception as e:
            log_debug(f"[ERROR] Failed to process ARP entry {entry}: {e}")
            log_debug(traceback.format_exc())