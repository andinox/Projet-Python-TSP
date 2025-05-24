#This file contains the basic functions that will be used in other scripts.
import subprocess as sbp
import datetime

def ping(ip):
    """
    function that pings an ip adress
    return True if ping is successful
    else return False
    """
    try:
        sbp.check_output(['ping', '-c', '1', ip], timeout=3)
        return True
    except Exception:
        return False




def traceroute(destination):
    try:
        output = sbp.check_output(['traceroute', '-n', '-m', '20', destination], stderr=sbp.STDOUT)
        lines = output.decode().splitlines()

        hops = []
        for line in lines[1:]:
            parts = line.split()
            if len(parts) >= 2 and parts[1] != '*':
                hops.append(parts[1])

        if hops:
            dernier_hop = hops[-1]
            return hops, dernier_hop
        else:
            return [], None
    except sbp.CalledProcessError as e:
        return [], None

