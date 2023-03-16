from django.contrib import admin
from .forms import MovimentoFormAdmin
import datetime



# Register your models here.
from .models import PagarReceber, MovimentosCaixa, ArquivosContabeis
from django.contrib.admin.filters import SimpleListFilter

class FiltroPagamentos(SimpleListFilter):
    parameter_name = "Pagamentos"
    title = "Pagamentos"
    
    def lookups(self, request, model_admin):
        return(('pgto_aberto_recente', 'Próximos Pagamentos'),
               ('pgto_vencidos', 'Pagamentos Atrasados'))
        #return super().lookups(request, model_admin)
    
    def queryset(self, request, queryset):
        today = datetime.date.today()
        begin = today + datetime.timedelta(days=-7)
        end = today + datetime.timedelta(days=7)
        if self.value() == 'pgto_aberto_recente':
            return queryset.filter(especie__tipo = 'O').filter(data_vcto__gte = begin).filter(data_vcto__lte = end).filter(status__in =['AB', 'PP'])
        if self.value() == 'pgto_vencidos':
            return queryset.filter(especie__tipo = 'O').filter(data_vcto__lt = today).filter(status__in =['AB', 'PP'])

class FiltroRecebimentos(SimpleListFilter):
    parameter_name = "Recebimentos"
    title = "Recebimentos"
    
    def lookups(self, request, model_admin):
        return(('pgto_aberto_recente', 'Próximos Pagamentos'),
               ('pgto_vencidos', 'Pagamentos Atrasados'))
        #return super().lookups(request, model_admin)
    
    def queryset(self, request, queryset):
        today = datetime.date.today()
        begin = today + datetime.timedelta(days=-7)
        end = today + datetime.timedelta(days=7)
        if self.value() == 'pgto_aberto_recente':
            return queryset.filter(especie__tipo = 'D').filter(data_vcto__gte = begin).filter(data_vcto__lte = end).filter(status__in =['AB', 'PP'])
        if self.value() == 'pgto_vencidos':
            return queryset.filter(especie__tipo = 'D').filter(data_vcto__lt = today).filter(status__in =['AB', 'PP'])





class MovimentoAdmin(admin.ModelAdmin):
    form = MovimentoFormAdmin

    class Media:
        js = ("jquery-3.6.3.min.js","form.js",)


# Register your models here.
@admin.register(PagarReceber)
class PagarReceberAdmin(admin.ModelAdmin):
    list_display = ('data_vcto', 'descricao', )
    list_filter =(FiltroPagamentos, FiltroRecebimentos )

 

admin.site.register(MovimentosCaixa, MovimentoAdmin)
admin.site.register(ArquivosContabeis)