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



def save_arp_entries_to_db(entries):
    for entry in arp_entries:
        try:
            # link with the interface based on the idinterface
            interface = Interface.objects.get(interface_index=entry["idinterface"])

            ARPEntry.save(
                ip_arp=entry["ip_arp"],
                idinterface=interface
            )

        except Interface.DoesNotExist:
            print(f"[WARN] Interface avec index {entry['idinterface']} introuvable.")
        except Exception as e:
            print(f"[ERREUR] Insertion ARP : {e}")
