from django.contrib import admin

from core.models import *

class RouteurAdmin(admin.ModelAdmin):
    list_display=("name","ip","status",)

class DiagnosticAdmin(admin.ModelAdmin):
    list_display=("routeur","type_diagno","resultat","date",)

class ScenarioAdmin(admin.ModelAdmin):
    list_display=("nom","description",)
admin.site.register(Routeur,RouteurAdmin,)
admin.site.register(Diagnostic,DiagnosticAdmin,)
admin.site.register(Scenario,ScenarioAdmin,)
