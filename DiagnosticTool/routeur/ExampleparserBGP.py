def convert_bgp_state(state):
    #si jamais ce n'est pas Up mais Established l'état
    return "Up" if state.upper() == "ESTABLISHED" else "Down"

def parse_bgp_notification(notification):
    # Dictionary to collect BGP neighbor entries grouped by their IP address
    bgp_entries = {}

    # Extract the 'update' part of the gNMI notification, which contains the changed values
    updates = notification.get("update", {})

    # Iterate through each path/value in the update
    for path, value in updates.items():
        # Use regular expression to extract the neighbor IP address from the path
        match = re.search(r'neighbor\[neighbor-address=([^\]]+)\]', path)
        if not match:
            continue  # If no neighbor IP is found, skip this entry

        neighbor_ip = match.group(1)  # Extract the IP address (e.g., 192.0.2.1)

        # Initialize the neighbor's dictionary entry if it's the first time we see this IP
        if neighbor_ip not in bgp_entries:
            bgp_entries[neighbor_ip] = {"NeighborIP": neighbor_ip}

        # Check the type of information this path provides and store it accordingly
        if path.endswith("peer-as"):
            bgp_entries[neighbor_ip]["ASN"] = value  
        elif path.endswith("session-state"):
            bgp_entries[neighbor_ip]["Up_down_status"] = convert_bgp_state(value)  # Convert state to "Up"/"Down"
        elif path.endswith("uptime"):
            bgp_entries[neighbor_ip]["timeStatus"] = value  # voir si on ne fait pas une fonction pour rendre ça plus lisible

    # Return the list of parsed neighbor entries
    return list(bgp_entries.values())
