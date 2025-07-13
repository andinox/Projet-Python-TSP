import ipaddress
from datetime import timedelta
from django.utils.timezone import now
from core.models import ARP_CONF, ARP_TEST

def check_arp_test_has_data():
    """
    Check if ARP_TEST table has any entries
    Returns:
            bool: False if any problem was detected during the tests.
            str: Report of the test.
    """
    one_minute_ago = now() - timedelta(minutes=1)
    count = ARP_TEST.objects.filter(timestamp__gte=one_minute_ago).count()
    if count == 0:
        return False, "[ECHEC] Aucun enregistrement trouvé dans la table ARP. \n [Ticket] Erreur détectée côté LAN."
    else:
        return True, f"[OK] {count} enregistrements trouvés dans la table ARP récente."
        

def check_arp_ip_in_interface_network():
    """
    Vérifie que chaque IP ARP de ARP_TEST est bien dans le réseau associé à son interface.
    Retourne :
        bool : False s’il y a un problème.
        list[str] : messages du rapport.
    """
    messages = []
    errors = 0
    one_minute_ago = now() - timedelta(minutes=1)

    # Préchargement de l'interface pour éviter les requêtes multiples
    entries = ARP_TEST.objects.select_related("idinterface").filter(timestamp__gte=one_minute_ago)

    if not entries.exists():
        messages.append("[ATTENTION] Aucun enregistrement ARP récent (moins de 1 minute) trouvé.")
        return False, messages

    for entry in entries:
        interface = entry.idinterface
        arp_ip = entry.ip_arp

        ip_addr = interface.ip_address
        mask = interface.subnet_mask

        if not ip_addr or not mask:
            messages.append(f"[AVERTISSEMENT] Interface {interface.idinterface} sans IP ou masque.")
            errors += 1
            continue

        try:
            network = ipaddress.ip_interface(f"{ip_addr}/{mask}").network
            arp_ip_obj = ipaddress.ip_address(arp_ip)

            if arp_ip_obj not in network:
                messages.append(
                    f"[ERREUR] ARP IP {arp_ip} hors du réseau {network} (interface {interface.idinterface})."
                )
                errors += 1
            else:
                messages.append(
                    f"[OK] ARP IP {arp_ip} dans le réseau {network} (interface {interface.idinterface})."
                )
        except Exception as e:
            messages.append(
                f"[ERREUR] Vérification impossible pour {arp_ip} (interface {interface.idinterface}) : {e}"
            )
            errors += 1

    if errors == 0:
        messages.append("[INFO] Tous les ARP IP sont dans leur réseau respectif.")
        return True, messages
    else:
        messages.append(f"[ECHEC] {errors} erreurs détectées lors de la vérification des IP ARP.")
        messages.append(f"[Ticket] Erreur détectée côté LAN.")
        return False, messages


def compare_arp_conf_and_test(interface_conf_map):
    """
    Compare ARP_CONF aux entrées de ARP_TEST de la dernière minute
    
    Args:
        interface_conf_map (dict):{idinterface: Interface_CONF} map.
    
    Returns:
        list[str]:message du rapport.
    """
    differences = 0
    messages = []
    messages.append("Comparaison entre la table ARP initiale et les entrées ARP_TEST récentes :")

    one_minute_ago = now() - timedelta(minutes=1)

    # Load only recent ARP_TEST entries
    arp_test_entries = ARP_TEST.objects.select_related("idinterface").filter(timestamp__gte=one_minute_ago)
    arp_conf_entries = ARP_CONF.objects.select_related("idinterface").all()

    # Build sets of (idinterface, ip_arp)
    conf_keys = {(entry.idinterface.idinterface, entry.ip_arp) for entry in arp_conf_entries}
    test_keys = {(entry.idinterface.idinterface.idinterface, entry.ip_arp) for entry in arp_test_entries}

    # Entries missing from ARP_TEST
    for key in conf_keys - test_keys:
        idinterface, ip = key
        interface = interface_conf_map.get(idinterface) 
        name = interface.interface_name if interface else f"ID {idinterface}"
        messages.append(f"[DIFF] ARP_CONF {ip} (interface {name}) non trouvé dans ARP_TEST (récente).")
        differences += 1

    # New entries in ARP_TEST that don't exist in ARP_CONF
    for key in test_keys - conf_keys:
        idinterface, ip = key
        interface = interface_conf_map.get(idinterface)
        name = interface.interface_name if interface else f"ID {idinterface}"
        messages.append(f"[INFO] ARP_TEST {ip} (interface {name}) non trouvé dans ARP_CONF (peut être normal).")

    # Summary
    if differences == 0:
        messages.append("[INFO] Toutes les IP ARP initiales sont présentes dans les données ARP récentes.")
    else:
        messages.append(f"[RÉSUMÉ] {differences} IP manquantes dans ARP_TEST récent comparé à ARP_CONF.")

    return messages






