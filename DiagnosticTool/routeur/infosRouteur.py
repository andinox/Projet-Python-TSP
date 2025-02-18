from DiagnosticTool.settings import ROUTEUR_PWD, ROUTEUR_USERNAME

#info pour se connecter au routeur
#à supp après prcq ct pour gnmi de base
hosts = [
    {
        "ip_address": "IP",
        "nos": "Cisco-xr",
        "port": 57400,
        "username": ROUTEUR_USERNAME,
        "password": ROUTEUR_PWD
    }
]
