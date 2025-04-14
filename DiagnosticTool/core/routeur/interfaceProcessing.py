#!/usr/bin/env python3

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

    # mapping interface_index -> ip_address
    interface_ip_map = {}
    for m in json_data["metrics"]:
        if m.get("name") == "interface_ip":
            f = m.get("fields", {})
            interface_index = f.get("interface_index")
            ip_address = f.get("ip_address")
            if interface_index is not None:
                interface_ip_map[interface_index] = ip_address

    # interfaces general parsing
    for m in json_data["metrics"]:
        if m.get("name") == "interface_status":
            f = m.get("fields", {})

            interface_index = f.get("interface_index")
            ip_address = interface_ip_map.get(interface_index, "0.0.0.0")

            parsed_entry = {
                "idInterface": interface_index,
                "interface": f.get("interface_name", "inconnu"),
                "admin": status_to_text(f.get("ifAdminStatus", -1)),
                "reachability": status_to_text(f.get("ifOperStatus", -1)),
                "interface_ip": ip_address
            }

            parsed_entries.append(parsed_entry)

    return parsed_entries
    
# SAVE INTERFACES
def save_interfaces_to_db(entries):
    log_debug(f"[DEBUG] Entries to save : {entries}")

    router = Router.objects.first() # We select the only router (at the moment) in the database, and we link it with the interfaces
    if not router:
        log_debug("[ERROR] Aucun routeur trouvé en base. Interfaces non sauvegardées.")
        return

    for entry in entries:
        try:
            interface_index=entry.get("interface_index")
            interface_name=entry.get("interface")
            admin_status=entry.get("admin")
            reachability=entry.get("reachability")
            interface_ip=entry.get("interface_ip")

            # Saving interface in DB using Django model
            interface = Interface(
                router=router,
                interface_name=interface_name,
                admin_status=admin_status,
                reachability=reachability,
                timestamp=now(),
                ip_address=interface_ip
            )

            interface.save()
            log_debug(f"[INFO] Interface '{interface_name}' avec IP '{interface_ip}' enregistrée.")

        except Exception as e:
            log_debug(f"[ERROR] Erreur pendant l'enregistrement de l'interface '{interface_name}': {e}")


