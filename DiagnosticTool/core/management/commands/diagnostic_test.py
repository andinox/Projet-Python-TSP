from django.core.management.base import BaseCommand
from core.scripts.basic_functions import ping, traceroute


class Command(BaseCommand):
    """
    Tested locally on the VM to debug
    """

    help = "Testing ping and traceroute functions towards an Ip address"

    def add_arguments(self, parser):
        parser.add_argument("ip_address", type=str, help="domain name or ip address")

    def handle(self, *args, **options):
        ip = options["ip_address"]
        self.stdout.write(self.style.NOTICE(f"Test of ping towards {ip}..."))

        if ping(ip):
            self.stdout.write(self.style.SUCCESS(f"OK  Ping towards {ip} success"))
        else:
            self.stdout.write(self.style.ERROR(f"NOK Ping towards {ip} failed"))

        self.stdout.write(self.style.NOTICE(f"Test of traceroute towards {ip}..."))
        hops, last_hop = traceroute(ip)
        if last_hop:
            self.stdout.write(
                self.style.SUCCESS(
                    f"OK Traceroute success : last hop reached -> {last_hop}"
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR(f"NOK Traceroute failed  or no hop detected")
            )

        self.stdout.write(self.style.SUCCESS("END --> Test finished"))
