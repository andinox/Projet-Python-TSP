from DiagnosticTool.settings import ROUTEUR_PORT,ROUTEUR_PWD, ROUTEUR_USERNAME

#info pour se connecter au router
#à modifier par rapport à la nouvelle vm
hosts = [
    {
        "ip_address": "IP", 
        "nos": "Cisco-xr",
        "port": ROUTEUR_PORT,
        "username": ROUTEUR_USERNAME,
        "password": ROUTEUR_PWD
    }
]