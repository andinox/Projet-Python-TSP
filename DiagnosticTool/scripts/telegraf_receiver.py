import os
import sys
import json
import django
import logging

# Configurer Django
sys.path.append("/home/user/Projet-Python-TSP/DiagnosticTool")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DiagnosticTool.settings")
django.setup()

from core.models.interface import Interface
from core.models.routeur import Routeur

# Configurer les logs
logging.basicConfig(
    filename="/home/user/Projet-Python-TSP/DiagnosticTool/logs/telegraf_receiver.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def telegraf_receiver():
    """
    Récupère les données envoyées par Telegraf via stdin et les insère en base de données.
    """
    try:
        # Lire les données envoyées par Telegraf
        input_data = sys.stdin.read().strip()
"""
        if not input_data:
            logging.warning("Aucune donnée reçue de Telegraf.")
            return

        logging.debug(f"JSON brut reçu : {input_data}")
"""
        # Décoder le JSON
        donnees = json.loads(input_data)

        # Récupération du nom et de l'IP du routeur
        routeur_name = donnees.get("routeur_name", "Inconnu")
        routeur_ip = donnees.get("routeur_ip", "0.0.0.0")

        as_bgp_value=donnees.get("as_bgp",0)
        routeur_next_hop=donnees.get("next_hop","0.0.0.0")
        if not routeur_next_hop:  # Si next_hop est vide ou absent, on met None explicitement
            routeur_next_hop = None
        # Vérifier si le routeur existe, sinon le créer
        routeur, _ = Routeur.objects.get_or_create(
            name=routeur_name,
            defaults={"ip": routeur_ip, "as_bgp": 0, "next_hop": routeur_next_hop}
        )

        # Traitement des interfaces
        for interface in donnees.get("interface_status", []):
            interface_name = interface.get("interface_name")
            oper_status = interface.get("oper_status")

            if not interface_name:
                logging.warning("Interface sans nom, ignorée.")
                continue

            # Conversion des statuts de l'interface
            status_map = {1: "up", 2: "down"}
            admin_status_text = status_map.get(interface.get("ifAdminStatus"), "unknown")
            oper_status_text = status_map.get(interface.get("ifOperStatus"), "unknown")

            # Insertion dans la base
            obj, created = Interface.objects.update_or_create(
                interface_name=interface.get("interface_name"),
                routeur=routeur,
                defaults={
                    "admin_status": admin_status_text,
                    "oper_status": oper_status_text,
                    "ip_address": donnees.get("routeur_ip", None),
                },
            )

            """if created:
                logging.info(f"Nouvelle interface ajoutée : {obj.interface_name} ({routeur.name})")
            else:
                logging.info(f"Interface mise à jour : {obj.interface_name} ({routeur.name})")
          
    except json.JSONDecodeError:
        logging.error("Erreur : Impossible de décoder le JSON reçu")
    except Exception as e:
        logging.error(f"Erreur lors du traitement des données : {e}")
"""
if __name__ == "__main__":
    telegraf_receiver()
