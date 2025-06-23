from DiagnosticTool.settings import ROUTER_PWD, ROUTER_USERNAME, ROUTER_IP

#info to connect to the router

hosts = [
    {
        "ip_address": ROUTER_IP, 
        "nos": "Cisco-xr",
        "port": 57400,
        "username": ROUTER_USERNAME,
        "password": ROUTER_PWD
    }
]
