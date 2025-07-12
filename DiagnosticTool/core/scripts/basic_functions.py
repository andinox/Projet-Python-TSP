#This file contains the basic functions that will be used in other scripts.
import nmap
from netmiko import ConnectHandler
from core.router import hosts
import os
def get_router_connection():
    """
    returns the router connection details
    """
    return hosts[0]

def ping(ip, count=5, timeout=2, source=os.getenv('ROUTER_IP')):
    """
    Sends an interactive ping from the router to the given IP address,
    using optional source IP. Returns True if ping is successful.
    """
    try:
        conn = ConnectHandler(**get_router_connection())
        conn.enable()
        output = conn.send_command_timing("ping")
        output += conn.send_command_timing("")  # Protocol [ip]
        output += conn.send_command_timing(ip)  # Target IP
        output += conn.send_command_timing(str(count))  # Repeat count
        output += conn.send_command_timing("")  # Datagram size
        output += conn.send_command_timing(str(timeout))  # Timeout
        output += conn.send_command_timing("yes")  # Extended commands? yes
        output += conn.send_command_timing("no")  # Ingress ping? no
        output += conn.send_command_timing(source if source else "")  # Source address
        output += conn.send_command_timing("")  # DSCP
        output += conn.send_command_timing("")  # TOS
        output += conn.send_command_timing("")  # DF bit
        output += conn.send_command_timing("")  # Validate reply
        output += conn.send_command_timing("")  # Data pattern
        output += conn.send_command_timing("")  # LSR/Timestamp/etc
        output += conn.send_command_timing("")  # Sweep range

        conn.disconnect()

        print("[DEBUG ping output]:\n", output)
        return "!" in output
    except Exception as e:
        print(f"[ERROR ping] : {e}")
        return False



def traceroute(destination):
    """
    executes a traceroute from the router to the given destination
    returns a list of hops and the last hop if available
    if failure then returns ([], None)
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

def nmap_scan(ip_address):
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

def convert_uptime(uptime_centisecs):
    """
    Convert uptime from centiseconds to days, hours, minutes, seconds.
    """
    total_seconds = int(uptime_centisecs) // 100
    days = total_seconds // 86400
    hours = (total_seconds % 86400) // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{days}d {hours}h {minutes}m {seconds}s"
