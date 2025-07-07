#This file contains the basic functions that will be used in other scripts.
import datetime
import nmap
import re
from netmiko import ConnectHandler
from DiagnosticTool import settings
from core.router.infosrouter import hosts
from core.router.general_functions import log_debug

def get_router_connection():
    """
    returns the router connection details
    """
    return hosts[0]

def ping(ip, count=5, timeout=2, source="gigabitEthernet 1"):
    """
    function sending  a ping from the router to the given ip address
    returns True if ping is successful
    else returns False
    """
    try:
        conn = ConnectHandler(**get_router_connection())

        # On tente d'envoyer un ping direct avec count et timeout
        output = conn.send_command(f"ping {ip} repeat {count} timeout {timeout} source {source}")

        # Si le routeur est en mode interactif
        if "Protocol" in output:
            output = conn.send_command_timing("ping")
            output += conn.send_command_timing("")  # Protocol [ip]
            output += conn.send_command_timing(ip)  # Target IP
            output += conn.send_command_timing(str(count))  # Repeat count
            output += conn.send_command_timing("")  # Datagram size
            output += conn.send_command_timing(str(timeout))  # Timeout in seconds
            output += conn.send_command_timing("yes")  # Extended commands: yes
            output += conn.send_command_timing(source)  # Source address
            for _ in range(6):
                output += conn.send_command_timing("")  # Skip remaining extended options

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

def get_open_ports(ip_address):
    nm = nmap.PortScanner()
    nm.scan(ip_address, arguments='-sV')

    results = {}
    if ip_address in nm.all_hosts():
        for proto in nm[ip_address].all_protocols():
            service_info = []

            for port in sorted(nm[ip_address][proto].keys()):
                port_data = nm[ip_address][proto][port]
                version = port_data.get("version", "")
                product = port_data.get("product", "")
                name = port_data.get("name", "")
                extrainfo=port_data.get("extrainfo","")

                service_info.append({
                    "port": port,
                    "name": name,
                    "product": product,
                    "version": version,
                    "extrainfo":extrainfo
                })

            results[proto] = service_info

    return results