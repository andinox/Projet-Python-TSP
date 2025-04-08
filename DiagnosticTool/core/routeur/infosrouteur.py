from DiagnosticTool.settings import ROUTEUR_PWD, ROUTEUR_USERNAME

#info pour se connecter au routeur
#à modifier par rapport à la nouvelle vm
hosts = [
    {
        "ip_address": "IP", 
        "nos": "Cisco-xr",
        "port": 57400,
        "username": ROUTEUR_USERNAME,
        "password": ROUTEUR_PWD
    }
]
