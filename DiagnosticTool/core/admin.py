from django.contrib import admin

from core.models.router import Router
from core.models.diagnostic import Diagnostic
from core.models.scenario import Scenario
from core.models.interface import Interface


class RouterAdmin(admin.ModelAdmin):
    list_display=("name","next_hop","as_bgp","user")

class DiagnosticAdmin(admin.ModelAdmin):
    list_display=("router","diagnosis_type","result","date",)

class ScenarioAdmin(admin.ModelAdmin):
    list_display=("name","description","slug",)

class InterfaceAdmin(admin.ModelAdmin):
    list_display = ("interface_name", "router", "admin_status", "oper_status", "ip_address", "timestamp")
    search_fields = ("interface_name", "ip_address")
    list_filter = ("admin_status", "oper_status")

admin.site.register(Router,RouterAdmin,)
admin.site.register(Diagnostic,DiagnosticAdmin,)
admin.site.register(Scenario,ScenarioAdmin,)
admin.site.register(Interface,InterfaceAdmin)