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
