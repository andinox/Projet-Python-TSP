#!/usr/bin/env python

from netmiko import ConnectHandler

# Paramètres
device = {
    'device_type': 'cisco_ios',
    'ip': '172.16.10.51',
    'username': 'admin',
    'password': 'dkSDwa80f13faXcwxzj',
    # 'secret': 'enable_password',
}

# Connexion au routeur
try:
    net_connect = ConnectHandler(**device)
    # net_connect.enable()

    # Exécution d'une commande
    output = net_connect.send_command('show ip arp')
    print("Résultat de la commande :\n", output)

    net_connect.disconnect()

except Exception as e:
    print("Erreur lors de la connexion SSH")