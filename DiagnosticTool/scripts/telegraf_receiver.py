#!/usr/bin/env python3

import sys
import json

def main():
    for line in sys.stdin:
        try:
            with open("/tmp/telegraf_exec_test.log", "a") as f:
                f.write("Script appelé par Telegraf\n")
            data = json.loads(line)
            with open("/tmp/telegraf_metrics.json", "a") as f:
                f.write(json.dumps(data) + "\n")
            print("Nouveau paquet Telegraf reçu :")
            print(json.dumps(data, indent=2))

        except json.JSONDecodeError as e:
            print("Erreur de parsing JSON :", e)

if __name__ == "__main__":
    main()
