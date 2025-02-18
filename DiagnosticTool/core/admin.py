from django.contrib import admin

from core.models.routeur import Routeur
from core.models.diagnostic import Diagnostic
from core.models.scenario import Scenario


class RouteurAdmin(admin.ModelAdmin):
    list_display=("name","ip","status",)

class DiagnosticAdmin(admin.ModelAdmin):
    list_display=("routeur","type_diagno","resultat","date",)

class ScenarioAdmin(admin.ModelAdmin):
    list_display=("nom","description","slug",)

admin.site.register(Routeur,RouteurAdmin,)
admin.site.register(Diagnostic,DiagnosticAdmin,)
admin.site.register(Scenario,ScenarioAdmin,)
