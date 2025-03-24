def parse_bgp_from_json(json_data):
    parsed_entries = []

    neighbors = json_data.get("bgp", {}).get("neighbors", {})
    for ip, data in neighbors.items():
        entry = {
            "ASN": data.get("asn"),
            "NeighborIP": ip,
            "Up_down_status": data.get("state"),
            "timeStatus": data.get("uptime") #à adapter en fonction de ce qu'on a dans le json
        }
        parsed_entries.append(entry)

    return parsed_entries
