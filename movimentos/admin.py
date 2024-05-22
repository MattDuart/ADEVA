from django.contrib import admin
import re
from .forms import MovimentoFormAdmin
from django.utils.html import format_html
import datetime
import xlsxwriter
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
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
from .actions import print_recibo_lcto, gerar_excel_pagamentos, download_doc, print_selected, print_data_invoice
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
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
    actions = [print_recibo_lcto, gerar_excel_pagamentos, download_doc, print_selected, print_data_invoice]

    change_form_template = 'form_pagarreceber.html'
    add_form_template = 'form_pagarreceber.html'


    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        # Adiciona os parâmetros GET, exceto 'meu_campo_de_input', ao contexto
        extra_query_params = {k: v for k, v in request.GET.items() if k != 'concatenated_search'}
        extra_context['extra_query_params'] = extra_query_params
        return super().changelist_view(request, extra_context=extra_context)


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


    def response_change(self, request, obj):
        response = super().response_change(request, obj)
        if "_salvar_e_quitar" in request.POST:
            # Lógica para "Salvar e Quitar" na edição
            redirect_url = f'/admin/movimentos/movimentoscaixa/add/?lcto_ref={obj.pk}&origem=pagar_receber'
            return HttpResponseRedirect(redirect_url)
        return response

    def response_add(self, request, obj, post_url_continue=None):
        response = super().response_add(request, obj, post_url_continue)
        if "_salvar_e_quitar" in request.POST:
            # Lógica para "Salvar e Quitar" na adição
            redirect_url = f'/admin/movimentos/movimentoscaixa/add/?lcto_ref={obj.pk}&origem=pagar_receber'
            return HttpResponseRedirect(redirect_url)
        return response

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
            return format_html('<a class="button" href="{}">Quitar</a>', f'/admin/movimentos/movimentoscaixa/add/?lcto_ref={obj.pk}&origem=pagar_receber')
        elif pago == 'Restante':
            return format_html('<a class="button" href="{}">Quitar restante</a>', f'/admin/movimentos/movimentoscaixa/add/?lcto_ref={obj.pk}&origem=pagar_receber')
        else:
            return format_html('<a href="{}">Quitado</a>', f'/admin/movimentos/movimentoscaixa/?lcto_ref={obj.pk}')
    
    
    def formatar_data_vcto(self, obj):
        return obj.data_vcto.strftime('%d/%m/%Y')
    
    formatar_data_vcto.short_description = 'Data Vcto'


    campos_concatenados.short_description = 'Pessoa e Valor'
    botao_pagar.short_description = 'Quitar'

    


    list_display = ('formatar_data_vcto',  'campos_concatenados', 'descricao', 'nro_docto', 'especie')

    def get_list_display(self, request):
        list_display = super().get_list_display(request)
        # Verifique se o usuário tem a permissão desejada
        if request.user.has_perm('movimentos.change_movimentoscaixa'):
            # Adicione um campo extra na terceira posição
            list_display = list(list_display)  # Converta para lista, se ainda não for
            list_display.insert(2, 'botao_pagar')
        return list_display



    list_filter = ('especie', FiltroPagamentos, FiltroRecebimentos,
                   'data_atualizacao',  ('data_vcto', CustomDateRangeFilter), 'centro_custo', 'item_orcamento')
    search_fields = ('pessoa__nome', 'descricao', 'nro_docto', 'data_vcto', 'valor_docto')
    readonly_fields = ['valor_docto', 'valor_pago', 'status',
                       'data_criacao', 'data_atualizacao', 'usuario']
    
    def get_search_results(self, request, queryset, search_term):
        data_pattern = re.compile(r'(\d{2})/(\d{2})/(\d{4}|\d{2})')
        search_term = re.sub(data_pattern, self.format_date, search_term)
        # Substitui valores numéricos
        valor_pattern = re.compile(r'(\d{1,3}(?:\.\d{3})*),(\d{2})')
        search_term = re.sub(valor_pattern, lambda x: f"{x.group(1).replace('.', '')}.{x.group(2)}", search_term)

        print(search_term)

        # Executa a busca com o termo de busca modificado
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)

        return queryset, use_distinct

    def format_date(self, match):
        dia, mes, ano = match.groups()
        # Ajusta anos no formato DD/MM/AA para DD/MM/AAAA
        ano = '20' + ano if len(ano) == 2 else ano
        return f"{ano}-{mes}-{dia}"

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
            if lcto.nro_docto == None:
                lcto.nro_docto = ''

            historico = lcto.descricao  + ' - ' + lcto.nro_docto + ' - ' + lcto.data_vcto.strftime('%d/%m/%Y') + ' - ' + str(lcto.valor_docto) + ' - ' + lcto.pessoa.nome [0:300]
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

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        lcto_ref = request.GET.get('lcto_ref')
        if lcto_ref:
            queryset = queryset.filter(lcto_ref__id=lcto_ref)
        return queryset

    def get_changelist(self, request, **kwargs):
        return MyChangeList
    readonly_fields = ['data_criacao', 'data_atualizacao', 'usuario']

    def add_view(self, request, form_url='', extra_context=None):
        if 'origem' in request.GET:  # Ajuste conforme o nome real do parâmetro
            self.add_form_template = 'form_movimentos.html'
        else:
            self.add_form_template = None  # Usa o template padrão se não houver 'origem'
        return super().add_view(request, form_url, extra_context)
    
    def response_add(self, request, obj):
        print(request.POST)
        response = super().response_add(request, obj)
        if "_quitar" in request.POST:
            print("Quitar")
            # Redirecionar para a URL desejada após salvar
            return HttpResponseRedirect("/admin/movimentos/pagarreceber/")
        return response

    class Media:
        js = ("jquery-3.6.3.min.js", "form.js",)

# admin.site.register(MovimentosCaixa, MovimentoAdmin)
# admin.site.register(ArquivosContabeis)
