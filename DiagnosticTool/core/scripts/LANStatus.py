import ipaddress
from datetime import timedelta
from django.utils.timezone import now
from core.models import ARP_CONF, ARP_TEST, Interface_TEST

def check_arp_test_has_data():
    """
    Check if ARP_TEST table has any entries
    Returns:
            bool: False if any problem was detected during the tests.
            str: Report of the test.
    """
    count = ARP_TEST.objects.count()
    if count == 0:
        return False, "[ERREUR] Aucun enregistrement trouvé dans la table ARP."
    else:
        return True, f"[INFO] {count} enregistrements trouvés dans la table ARP."
        

def check_arp_ip_in_interface_network():
    """
    For each ARP_TEST entry, check if the IP is in the same network as its interface
    Returns:
            bool: False if any problem was detected during the tests.
            messages (str): Report of the test.
    """
    messages = []
    errors = 0
    ten_minutes_ago = now() - timedelta(minutes=1)

    entries = ARP_TEST.objects.select_related("idinterface").filter(timestamp__gte=ten_minutes_ago)
    
    if not entries.exists():
        messages.append("[ATTENTION] Aucun enregistrement ARP récent (moins de 1 minute) trouvé.")
        return False, messages
    #just checking if the last entry is correct
    for entry in entries:
        interface = entry.idinterface
        arp_ip = entry.ip_arp

        if not interface.ip_address or not interface.subnet_mask:
            messages.append(f"[AVERTISSEMENT] Interface {interface.idinterface} sans IP ou masque.")
            errors += 1
            continue

        try:
            #transforming the information from the database into network objects so that we can check if an IP is in the good network 
            network = ipaddress.ip_interface(f"{interface.ip_address}/{interface.subnet_mask}").network
            arp_ip_obj = ipaddress.ip_address(arp_ip)
            if arp_ip_obj not in network:
                messages.append(f"[ERREUR] ARP IP {arp_ip} hors du réseau {network} (interface {interface.idinterface}).")
                errors += 1
            else:
                messages.append(f"[OK] ARP IP {arp_ip} dans le réseau {network} (interface {interface.idinterface}).")
        except Exception as e:
            messages.append(f"[ERREUR] Vérification impossible pour {arp_ip} (interface {interface.idinterface}) : {e}")
            errors += 1

    if errors == 0:
        messages.append("[INFO] Tous les ARP IP sont dans leur réseau respectif.")
        return True, messages
    else:
        messages.append(f"[RÉSUMÉ] {errors} erreurs détectées lors de la vérification que les IP dans la table ARP sont dans le bon réseau.")
        return False, messages



def compare_arp_conf_and_test():
    """
    Compare ARP_CONF and ARP_TEST tables, and print differences
    Returns:
            str: Report of the test.
    """
    differences = 0
    messages = []
    messages.append(" Comparaison entre la table ARP initiale et la table ARP actuelle : ")

    # listing the entries only once and saving them in the memory
    arp_conf_entries = list(ARP_CONF.objects.select_related("idinterface").all())
    arp_test_entries = list(ARP_TEST.objects.select_related("idinterface").all())

    # creating sets to compare more efficiently
    conf_keys = {(entry.idinterface.idinterface, entry.ip_arp) for entry in arp_conf_entries}
    test_keys = {(entry.idinterface.idinterface, entry.ip_arp) for entry in arp_test_entries}

    # step 1 : check that every ARP_CONF entries are in ARP_TEST
    for key in conf_keys:
        if key not in test_keys:
            idinterface, ip = key
            messages.append(f"[DIFF] ARP_CONF {ip} (interface {idinterface}) non trouvé dans ARP_TEST.")
            differences += 1

    # step 2 : list ARP_TEST not in ARP_CONF
    for key in test_keys:
        if key not in conf_keys:
            idinterface, ip = key
            messages.append(f"[INFO] ARP_TEST {ip} (interface {idinterface}) non trouvé dans ARP_CONF (peut être normal).")

    # summary
    if differences == 0:
        messages.append("[INFO] Toutes les entrées dans la table ARP initiale sont présentes dans la table ARP actuelle.")
    else:
        messages.append(f"[RÉSUMÉ] {differences} entrées ARP_CONF manquantes dans ARP_TEST.")

    return messages


