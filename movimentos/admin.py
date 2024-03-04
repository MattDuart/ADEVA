from django.contrib import admin
from .forms import MovimentoFormAdmin
from django.utils.html import format_html
import datetime
import xlsxwriter
from django.http import HttpResponse
from django.db import models
from rangefilter.filters import DateRangeFilter, DateTimeRangeFilter, NumericRangeFilter
from django.db.models import Q
from django.contrib.admin.filters import DateFieldListFilter
from django.contrib.admin.views.main import ChangeList

# Register your models here.
from .models import PagarReceber, MovimentosCaixa, RecibosMaster, LctoDetalhe, OutrosArquivosLcto
from configuracoes.models import Contas
from django.contrib.admin.filters import SimpleListFilter
from django.db.models import Sum
from .actions import print_recibo_lcto, gerar_excel_pagamentos, download_doc, print_selected


class FiltroPagamentos(SimpleListFilter):
    parameter_name = "Pagamentos"
    title = "Pagamentos"

    def lookups(self, request, model_admin):
        return (('pgto_aberto_recente', 'Pagamentos Próximos 7 dias'),
                ('pgto_vencidos', 'Pagamentos Atrasados'))
        # return super().lookups(request, model_admin)

    def queryset(self, request, queryset):
        today = datetime.date.today()
        begin = today + datetime.timedelta(days=-7)
        end = today + datetime.timedelta(days=7)
        if self.value() == 'pgto_aberto_recente':
            return queryset.filter(especie__tipo='O').filter(data_vcto__gte=begin).filter(data_vcto__lte=end).filter(status__in=['AB', 'PP'])
        if self.value() == 'pgto_vencidos':
            return queryset.filter(especie__tipo='O').filter(data_vcto__lt=today).filter(status__in=['AB', 'PP'])


class FiltroRecebimentos(SimpleListFilter):
    parameter_name = "Recebimentos"
    title = "Recebimentos"

    def lookups(self, request, model_admin):
        return (('pgto_aberto_recente', 'Recebimentos Próximos 7 dias'),
                ('pgto_vencidos', 'Recebimentos Atrasados'))
        # return super().lookups(request, model_admin)

    def queryset(self, request, queryset):
        today = datetime.date.today()
        begin = today + datetime.timedelta(days=-7)
        end = today + datetime.timedelta(days=7)
        if self.value() == 'pgto_aberto_recente':
            return queryset.filter(especie__tipo='D').filter(data_vcto__gte=begin).filter(data_vcto__lte=end).filter(status__in=['AB', 'PP'])
        if self.value() == 'pgto_vencidos':
            return queryset.filter(especie__tipo='D').filter(data_vcto__lt=today).filter(status__in=['AB', 'PP'])


class ContasFilter(SimpleListFilter):
    title = 'Contas'
    parameter_name = 'conta'

    def lookups(self, request, model_admin):
        qs = Contas.objects.all()
        return [(str(item.pk), str(item)) for item in qs]

    def queryset(self, request, queryset):
        if self.value():
            value = self.value()
            queryset = queryset.filter(
                Q(conta_origem__id=value) | Q(conta_destino__id=value)
            )
            return queryset


class MyChangeList(ChangeList):
    def get_filters(self, request):
        filters = super().get_filters(request)
        my_filter_value = request.GET.get('data_lcto__range__gte')

        new_filters = []

        if my_filter_value:
            # Se o filtro "my_change" estiver definido, remova o filtro "other_change".

            for f in filters[0]:
                if isinstance(f, DateFieldListFilter) == False:
                    new_filters.append(f)
        else:
            new_filters = filters[0]

        filters = list(filters)
        filters[0] = new_filters
        filters = tuple(filters)

        return filters


class CustomDateRangeFilter(DateRangeFilter):
    def __init__(self, *args, **kwargs):
        super(CustomDateRangeFilter, self).__init__(*args, **kwargs)


"""   
        self.used_parameters['data_lcto__gte'] = (datetime.now() - timedelta(weeks=-5000)).strftime('%Y-%m-%d')
        self.used_parameters['data_lcto__lt'] = (datetime.now() - timedelta(weeks=5000)).strftime('%Y-%m-%d')

        def queryset(self, request, queryset):
            # Usa os novos valores de start_date e end_date para filtrar o queryset
            queryset = super(CustomDateRangeFilter, self).queryset(request, queryset)
            return queryset
"""

# Register your models here.


class LctoDetalheInline(admin.TabularInline):
    model = LctoDetalhe
    extra = 2

class OutrosArquivosInline(admin.TabularInline):
    model = OutrosArquivosLcto
    extra = 2
@admin.register(PagarReceber)
class PagarReceberAdmin(admin.ModelAdmin):
    inlines = [OutrosArquivosInline, LctoDetalheInline,]
    actions = [print_recibo_lcto, gerar_excel_pagamentos, download_doc, print_selected]

    def save_model(self, request, obj, form, change):
        usuario_logado = request.user
        obj.usuario = usuario_logado
        obj.save()

    def campos_concatenados(self, obj):
        return f"{obj.pessoa} --- {obj.valor_docto}"
    
    def botao_pagar(self, obj):
        #if self.user_has_permission:  # Substitua pela lógica de permissão
        pago = None
        movimento = MovimentosCaixa.objects.filter(lcto_ref=obj)
        if movimento.count() == 0:
            pago = 'Pagar'
        else:
        
            valor = 0
            for item in movimento:
                valor += item.valor

            if valor < obj.valor_docto:
                pago = 'Restante'

        if pago == 'Pagar':
            return format_html('<a class="button" href="{}">Pagar</a>', f'/admin/movimentos/movimentoscaixa/add/?lcto_ref={obj.pk}')
        elif pago == 'Restante':
            return format_html('<a class="button" href="{}">Pagar restante</a>', f'/admin/movimentos/movimentoscaixa/add/?lcto_ref={obj.pk}')
        else:
            return 'Pago'
    
    
    def formatar_data_vcto(self, obj):
        return obj.data_vcto.strftime('%d/%m/%Y')
    
    formatar_data_vcto.short_description = 'Data Vcto'


    campos_concatenados.short_description = 'Pessoa e Valor'
    botao_pagar.short_description = 'Pagar'

    list_display = ('formatar_data_vcto',  'campos_concatenados', 'botao_pagar','descricao', 'especie')
    list_filter = ('especie', FiltroPagamentos, FiltroRecebimentos,
                   'data_atualizacao',  ('data_vcto', CustomDateRangeFilter), 'centro_custo', 'item_orcamento')
    readonly_fields = ['valor_pago', 'status',
                       'data_criacao', 'data_atualizacao', 'usuario']
    

    class Media:
        css = {
            'all': ('movimentos.css',)
        }



@admin.register(MovimentosCaixa)
class MovimentoAdmin(admin.ModelAdmin):
    form = MovimentoFormAdmin
    actions = [download_doc,]

    def save_model(self, request, obj, form, change):
        usuario_logado = request.user
        obj.usuario = usuario_logado
        obj.save()

    list_per_page = 200
    list_display = ("__str__",)
    list_filter = (
        ContasFilter, 'data_lcto', ('data_lcto', CustomDateRangeFilter),
    )

    def get_changelist(self, request, **kwargs):
        return MyChangeList
    readonly_fields = ['data_criacao', 'data_atualizacao', 'usuario']

    class Media:
        js = ("jquery-3.6.3.min.js", "form.js",)

# admin.site.register(MovimentosCaixa, MovimentoAdmin)
# admin.site.register(ArquivosContabeis)
