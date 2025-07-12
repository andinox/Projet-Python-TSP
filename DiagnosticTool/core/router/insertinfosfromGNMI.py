
from infosrouter import hosts
from gnmi_bgp_parser import parse_bgp_notification

# Paramètres du routeur
host = hosts[0]
target = (host["ip_address"], host["port"])

# Chemins OpenConfig à surveiller
paths = [
    '/network-instances/network-instance[name=default]/protocols/protocol[name=BGP][identifier=BGP]/bgp/neighbors'
]

# Connexion et souscription gNMI
with gNMIclient(target=target, username=host["username"], password=host["password"], insecure=True) as client:
    
    sub_request = {
        'subscription': [
            {
                'path': path,
                'mode': 'on_change',
                'sample_interval': 0 #nécessaire sur les Cisco-xr même si c'est on change
            } for path in paths
        ],
        'mode': 'stream',
        'encoding': 'json'
    }

    for notif in client.subscribe(subscribe=sub_request):
        bgp_entries = parse_bgp_notification(notif)

        # voir comment inserer dans django
