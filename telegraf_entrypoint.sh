#!/bin/bash
set -e

OPENVPN_CONFIG="/vpn/fisa-python-nriedel.ovpn"

if [ -f "$OPENVPN_CONFIG" ]; then
    openvpn --config "$OPENVPN_CONFIG" &
    VPN_PID=$!
    # give VPN a moment to establish
    sleep 10
fi

exec telegraf --config /etc/telegraf/telegraf.conf
