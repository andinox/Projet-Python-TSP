import json

file_path = "/var/log/telegraf/interfaces.out"


# Lecture du fichier json contenant les informations sur les statuts des interfaces
def read_metrics(file_path):
    with open(file_path, "r") as f:
        for line in f:
            data = json.loads(line.strip())
            affichage_json = json.dumps(data, indent=2)
            print(affichage_json)

#Avec filtre des champs qui nous intressenté
def filtre_status(file_path):
    with open(file_path, "r") as f:
        for line in f:
            data = json.loads(line.strip())
            # Extraction information
            interface_name = data["tags"]["name"]
            admin_status = data["fields"].get("admin_status")
            op_status = data["fields"].get("op_status")

            # Affichage
            print("Interface : ", interface_name)
            print("Admin Status : ", admin_status)
            print("Operational Status : ", op_status)
            print("----------------------------------------")


if __name__ == "__main__":
    filtre_status(file_path)
