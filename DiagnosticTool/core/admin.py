from django.contrib import admin
from core.models.router import Router
from core.models.diagnostic import Diagnostic
from core.models.scenario import Scenario
from core.models.interface import *
from core.models.arp import *
from core.models.bgp import *
from core.models.security import Security
from core.models.securityscan import SecurityScan


class RouterAdmin(admin.ModelAdmin):
    list_display = ("name", "next_hop", "all_users")

    def all_users(self, obj):
        """
        Return all users associated to this router
        """
        usernames = []
        for user in obj.users.all():
            usernames.append(user.username)
        return ", ".join(usernames)


class DiagnosticAdmin(admin.ModelAdmin):
    list_display = (
        "router",
        "diagnosis_type",
        "result",
        "date",
    )


class ScenarioAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "slug")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}


class InterfaceConfAdmin(admin.ModelAdmin):
    list_display = (
        "idinterface",
        "interface_name",
        "router",
        "admin_status",
        "reachability",
        "ip_address",
        "subnet_mask",
        "timestamp",
    )
    search_fields = ("interface_name", "ip_address")
    list_filter = ("admin_status", "reachability")


class InterfaceTestAdmin(admin.ModelAdmin):
    list_display = (
        "interface_name",
        "router",
        "admin_status",
        "reachability",
        "ip_address",
        "subnet_mask",
        "timestamp",
    )
    search_fields = ("interface_name", "ip_address")
    list_filter = ("admin_status", "reachability")


class ARPConfAdmin(admin.ModelAdmin):
    list_display = ("ip_arp",)
    search_fields = ("ip_arp",)


class ARPTestAdmin(admin.ModelAdmin):
    list_display = ("ip_arp",)
    search_fields = ("ip_arp",)


class BGPAConfAdmin(admin.ModelAdmin):
    list_display = ("asn", "neighbor_ip", "up_down_status", "time_last_change")
    search_fields = ("asn", "neighbor_ip", "up_down_status", "time_last_change")


class BGPTestAdmin(admin.ModelAdmin):
    list_display = ("asn", "neighbor_ip", "up_down_status", "time_last_change")
    search_fields = ("asn", "neighbor_ip", "up_down_status", "time_last_change")


class SecurityAdmin(admin.ModelAdmin):
    list_display = ("hostname", "sys_descr", "uptime", "cdp_enabled", "last_updated")
    search_fields = ("hostname", "sys_descr", "uptime", "cdp_enabled", "last_updated")


class SecurityScanAdmin(admin.ModelAdmin):
    list_display = (
        "security",
        "protocol",
        "port",
        "service_name",
        "product",
        "version",
        "extrainfo",
        "timestamp",
    )
    search_fields = (
        "security",
        "protocol",
        "port",
        "service_name",
        "product",
        "version",
        "extrainfo",
        "timestamp",
    )


admin.site.register(
    Router,
    RouterAdmin,
)

admin.site.register(
    Diagnostic,
    DiagnosticAdmin,
)

admin.site.register(
    Scenario,
    ScenarioAdmin,
)

admin.site.register(Interface_CONF, InterfaceConfAdmin)
admin.site.register(Interface_TEST, InterfaceTestAdmin)

admin.site.register(ARP_CONF, ARPConfAdmin)
admin.site.register(ARP_TEST, ARPTestAdmin)

admin.site.register(BGP_CONF, BGPAConfAdmin)
admin.site.register(BGP_TEST, BGPTestAdmin)

admin.site.register(Security, SecurityAdmin)

admin.site.register(SecurityScan, SecurityScanAdmin)
