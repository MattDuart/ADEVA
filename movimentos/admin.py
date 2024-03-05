from django.contrib import admin
from .forms import MovimentoFormAdmin
from django.utils.html import format_html
import datetime
import xlsxwriter
from django.http import HttpResponse, HttpRequest
from django.db import models
from rangefilter.filters import DateRangeFilter, DateTimeRangeFilter, NumericRangeFilter
from django.db.models import Q
from django.contrib.admin.filters import DateFieldListFilter
from django.contrib.admin.views.main import ChangeList
from django.forms.models import BaseInlineFormSet
# Register your models here.
from .models import PagarReceber, MovimentosCaixa, RecibosMaster, LctoDetalhe, OutrosArquivosLcto
from configuracoes.models import Contas
from django.contrib.admin.filters import SimpleListFilter
from django.db.models import Sum
from .actions import print_recibo_lcto, gerar_excel_pagamentos, download_doc, print_selected
from django.core.exceptions import ValidationError

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
class LctoDetalheFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        soma = 0
        tem_item = False

        for form in self.forms:
            if not form.is_valid():
                return  # Se um dos formulários não for válido, não continue

            if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                tem_item = True
                soma += form.cleaned_data.get('valor', 0)

        if not tem_item:
            raise ValidationError("Pelo menos um LctoDetalhe deve ser preenchido.")
        if soma == 0:
            raise ValidationError("A soma dos valores dos LctoDetalhe não pode ser zero.")

class LctoDetalheInline(admin.TabularInline):
    model = LctoDetalhe
    extra = 2
    formset = LctoDetalheFormSet

class OutrosArquivosInline(admin.TabularInline):
    model = OutrosArquivosLcto
    extra = 2
@admin.register(PagarReceber)
class PagarReceberAdmin(admin.ModelAdmin):
    inlines = [OutrosArquivosInline, LctoDetalheInline,]
    actions = [print_recibo_lcto, gerar_excel_pagamentos, download_doc, print_selected]

    def save_model(self, request, obj, form, change):
        # Marque o objeto como não salvo
        obj._pre_save_instance = obj
        # Não chame o save ainda


    def save_formset(self, request, form, formset, change):
        if formset.model == LctoDetalhe:
            instances = formset.save(commit=False)

            if not instances:
                formset._non_form_errors = formset.error_class(["Pelo menos um LctoDetalhe deve ser preenchido."])
                return  # Interrompe o salvamento dos dados

            soma = sum(instance.valor for instance in instances if instance.valor)
            if soma == 0:
                formset._non_form_errors = formset.error_class(["A soma dos valores dos LctoDetalhe não pode ser zero."])
                return  # Interrompe o salvamento dos dados

            # Verifique se a instância PagarReceber já foi salva
            pagar_receber_instance = form.instance
            if pagar_receber_instance:
                pagar_receber_instance.valor_docto = soma
                # Salvando a instância PagarReceber
                pagar_receber_instance.save()

            # Salvando cada instância de LctoDetalhe
            for instance in instances:
                instance.lcto_id = pagar_receber_instance.id
                instance.save()
        else:
            super().save_formset(request, form, formset, change)
  

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
#### colocar permissão
        if pago == 'Pagar':
            return format_html('<a class="button" href="{}">Quitar</a>', f'/admin/movimentos/movimentoscaixa/add/?lcto_ref={obj.pk}')
        elif pago == 'Restante':
            return format_html('<a class="button" href="{}">Quitar restante</a>', f'/admin/movimentos/movimentoscaixa/add/?lcto_ref={obj.pk}')
        else:
            return 'Quitado'
    
    
    def formatar_data_vcto(self, obj):
        return obj.data_vcto.strftime('%d/%m/%Y')
    
    formatar_data_vcto.short_description = 'Data Vcto'


    campos_concatenados.short_description = 'Pessoa e Valor'
    botao_pagar.short_description = 'Quitar'

    list_display = ('formatar_data_vcto',  'campos_concatenados', 'botao_pagar','descricao', 'especie')
    list_filter = ('especie', FiltroPagamentos, FiltroRecebimentos,
                   'data_atualizacao',  ('data_vcto', CustomDateRangeFilter), 'centro_custo', 'item_orcamento')
    readonly_fields = ['valor_docto', 'valor_pago', 'status',
                       'data_criacao', 'data_atualizacao', 'usuario']
    

    class Media:
        css = {
            'all': ('movimentos.css',)
        }
        js = ("form_pagar_receber.js",)



@admin.register(MovimentosCaixa)
class MovimentoAdmin(admin.ModelAdmin):
    form = MovimentoFormAdmin
    actions = [download_doc,]

    def save_model(self, request, obj, form, change):
        usuario_logado = request.user
        obj.usuario = usuario_logado
        obj.save()

    def get_changeform_initial_data(self, request: HttpRequest):
        initial = super().get_changeform_initial_data(request)
        lcto_ref = request.GET.get('lcto_ref')
        if lcto_ref:
            lcto = PagarReceber.objects.get(pk=lcto_ref)
            historico = lcto.descricao
            if lcto.especie.tipo == 'D':
                historico = f"Recebimento de {historico}"
                initial['tipo'] = 'PR'
            elif lcto.especie.tipo == 'O':
                historico = f"Pagamento de {historico}"
                initial['tipo'] = 'PG'
            else:
                historico = f"Transferência de {historico}"
                initial['tipo'] = 'TR'
           

            initial['valor'] = lcto.valor_docto - lcto.valor_pago  # 'campo_relacionado' deve ser substituído pelo nome real do campo
            initial['historico'] = historico
            initial['data_lcto'] = datetime.date.today().strftime('%d/%m/%Y')
        return initial

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
