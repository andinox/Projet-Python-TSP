#This file contains the basic functions that will be used in other scripts.
import datetime
from netmiko import ConnectHandler
from DiagnosticTool import settings
from core.router.infosrouter import hosts

def get_router_connection():
    """
    returns the router connection details
    """
    return hosts[0]

def ping(ip):
    """
    function sending  a ping from the router to the given ip address
    returns True if ping is successful
    else returns False    
    """
    try:
        conn = ConnectHandler(**get_router_connection())
        output = conn.send_command(f"ping {ip}")
        conn.disconnect()

        #Cisco ping output includes '!' for successful answers; it's seen as a True value
        return "!" in output
    except Exception as e:
        print(f"[ERROR ping] : {e}")
        return False


def traceroute(destination):
    """
    executes a traceroute from the router to the given destination
    returns a list of hops and the last hop if available
    if failur then returns ([], None)
    """
    try:
        conn = ConnectHandler(**get_router_connection())
        output = conn.send_command(f"traceroute {destination}")
        conn.disconnect()
        lines = output.splitlines()
        hops = []

        #extract the first valid ip from each line (skip '*')
        for l in lines:
            parts = l.split()
            for p in parts:
                if p.count('.') == 3 and p != '*':
                    hops.append(p)
                    break

        last_hop = hops[-1] if hops else None
        return hops, last_hop

    except Exception as e:
        print(f"[ERROR traceroute] : {e}")
        return [], None

