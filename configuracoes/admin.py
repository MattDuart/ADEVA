from django.contrib import admin

# Register your models here.
# Register your models here.
from .models import Especie, Contas, CentrosCustos, ItensOrcamento 

class ContasFormAction(admin.ModelAdmin):
    model = Contas
    
    class Media:
        js = ("jquery-3.6.3.min.js","form_pagarreceber.js",)


# Register your models here.
admin.site.register(Especie)
admin.site.register(Contas, ContasFormAction)
admin.site.register(CentrosCustos)
admin.site.register(ItensOrcamento)
