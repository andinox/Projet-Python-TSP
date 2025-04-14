#!/usr/bin/env python3

def status_to_text(val):
    return "up" if val==1 else "down"

# PARSING - INTERFACES
def parse_interface_from_json(json_data):
    parsed_entries=[]

    if "metrics" not in json_data:
        return parsed_entries
    
    for m in json_data["metrics"]:
        if m.get("name") == "interface_status":
            f=m.get("fields", {})
            
            parsed_entry={
                "idInterface":f.get("interface_index"),
                "interface":f.get("interface_name", "inconnu"), # inconnu by default
                "admin":status_to_text(f.get("ifAdminStatus", -1)), # -1 by default
                "reachability":status_to_text(f.get("ifOperStatus",-1)) # -1 by default
            }

            parsed_entries.append(parsed_entry)

    return parsed_entries
    
# SAVE INTERFACES
def save_interfaces_to_db(entries):
    hostInfos = '/home/user/Projet-Python-TSP/DiagnosticTool/core/routeur/infosrouter.py'

    for entry in entries:
        try:
            interface_index = entry.get("interface_index")
            interface_name = entry.get("interface")
            admin_status = entry.get("admin")
            reachability = entry.get("reachability")


            router_name_value = router_name(hostInfos) #retrieve router name from infosrouter.py
            
            if not router_name_value:
                print(f"[WARNING] Router name not found for interface '{interface_name}'")
                continue

            try:
                router = Router.objects.get(name=router_name_value) #create router object
            except Router.DoesNotExist:
                print(f"[ERROR] Router '{router_name_value}' not found in database. Skipping interface '{interface_name}'.")
                continue

            interface = Interface(
                router=router,
                interface_name=interface_name,
                admin_status=admin_status,
                reachability=reachability,
                timestamp=now()
            )

            interface.save()
            print(f"[INFO] Interface '{interface_name}' saved successfully for router '{router_name_value}'")

        except Exception as e:
            print(f"[ERROR] Unexpected error while saving interface '{entry.get('interface', 'Unknown')}': {e}")

