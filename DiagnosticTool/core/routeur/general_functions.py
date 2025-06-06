#!/usr/bin/env python3

def log_debug(message):
    with open('/tmp/debug_interfaces.log', 'a') as f:
        f.write(message + "\n")

