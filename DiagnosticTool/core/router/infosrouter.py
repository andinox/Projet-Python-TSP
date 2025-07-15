from DiagnosticTool.settings import ROUTER_PWD, ROUTER_USERNAME, ROUTER_IP, ENABLE

# info to connect to the router

hosts = [
    {
        "ip": ROUTER_IP,
        "device_type": "cisco_xr",
        "port": 22,
        "username": ROUTER_USERNAME,
        "password": ROUTER_PWD,
        "secret": ENABLE,
    }
]
