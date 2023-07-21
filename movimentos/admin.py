from django.contrib import admin
from .forms import MovimentoFormAdmin
import datetime
import xlsxwriter
from django.http import HttpResponse
from django.db import models
from rangefilter.filters import DateRangeFilter, DateTimeRangeFilter, NumericRangeFilter
from django.db.models import Q
from django.contrib.admin.filters import DateFieldListFilter
from django.contrib.admin.views.main import ChangeList

# Register your models here.
from .models import PagarReceber, MovimentosCaixa, ArquivosContabeis, RecibosMaster, ReciboDetalhe, LctoDetalhe
from configuracoes.models import Contas
from django.contrib.admin.filters import SimpleListFilter
from django.db.models import Sum
from .actions import print_recibo


"""
def calcula_saldo(id_conta='all', start_id=0):
    # usa star_id supondo que os movimentos são lançados em ordem de data
    # fazer por data poderia dat conflito se não forem escolhidos todos os lctos de uma data
    # na rotina por mês fechado esta função ficará mais adequada

    entradas = 0
    saidas = 0 

    if id_conta == 'all':
    
        tipos_entrada = ['SI', 'PR']
        entradas = MovimentosCaixa.objects.filter(id__lt=start_id,tipo__in=tipos_entrada).aggregate(Sum('valor'))['valor__sum']
        if entradas is None:
            entradas = 0
        tipos_saida = ['PG']
        saidas = MovimentosCaixa.objects.filter(id__lt=start_id, \
                                                    tipo__in=tipos_saida).aggregate(Sum('valor'))['valor__sum']
        if saidas is None:
            saidas  = 0
        
    else:

        entradas = MovimentosCaixa.objects.filter(id__lt=start_id, \
                                                         conta_destino=id_conta).aggregate(Sum('valor'))['valor__sum']
        if entradas is  None:
            entradas  = 0
    
        saidas = MovimentosCaixa.objects.filter(id__lt=start_id, \
                                                         conta_origem=id_conta).aggregate(Sum('valor'))['valor__sum']
        if saidas is None:
            saidas = 0

    print(entradas)
    print(saidas)
    
    saldo_inicial = entradas - saidas
    print(saldo_inicial)

    return saldo_inicial


@admin.action(description='Exportar para Excel')
def export_to_xlsx(modeladmin, request, queryset):


    opts = modeladmin.model._meta
    dateTimeObj = datetime.datetime.now()
    timestamp = dateTimeObj.strftime("%d-%b-%Y")
    content_disposition = f'attachment;filename=caixa_{timestamp}.xlsx'
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheet.sheet')
    response['Content-Disposition'] = content_disposition
    workbook = xlsxwriter.Workbook(response, {'in_memory': True})
    worksheet = workbook.add_worksheet()

    bold_format = workbook.add_format({'bold': True})

    menor_id = queryset.aggregate(menor_id=models.Min('id'))['menor_id']
 

    fields = [field for field in opts.get_fields()]


    header_list = []
    for field in fields:
        if field.name not in ['id', 'tipo', 'valor']:
            header_list.append(f'{field.verbose_name}')
    header_list.append("Projeto")
    header_list.append("Item Orçamentário")
    header_list.append("Entrada")
    header_list.append("Saída")
    header_list.append("Saldo")

    menor_id = queryset.aggregate(menor_id=models.Min('id'))['menor_id']
    
    if 'conta' not in request.GET:
        saldo = calcula_saldo(start_id=menor_id)        
    else:
        saldo = calcula_saldo(id_conta=int(request.GET.get('conta')), start_id=menor_id)

    for column, item in enumerate(header_list):
        worksheet.write(0, column, item, bold_format)

    worksheet.write(1,0,"SALDO INICIAL", bold_format)
    worksheet.write(1,len(header_list)-1,saldo, bold_format)
    linha = 0


    
    for row, obj in enumerate(queryset):
        if getattr(obj,'tipo') == 'TR' and 'conta' not in request.GET:
            continue

        data_row = []
        i = 0
        entrada = ''
        saida = ''


        for field in fields:
            value = getattr(obj, field.name)
            i += 1
            
            if field.name == 'valor':
                if getattr(obj, 'tipo') in ['SI', 'PR']:
                    saldo += value
                    entrada = value
                if getattr(obj, 'tipo') == 'PG':
                    saldo -= value
                    saida = value
                if getattr(obj, 'tipo') == "TR":
                                        
                    if getattr(obj,'conta_origem').id == int(request.GET.get('conta')):
                        saldo -= value
                        saida = value
                    if getattr(obj, 'conta_destino').id == int(request.GET.get('conta')):
                        saldo += value
                        entrada = value

            if value is None:
                value = ''


            if field.name == 'lcto_ref':
                if obj.lcto_ref is not None:
                    projeto = obj.lcto_ref.centro_custo
                    orcamento = obj.lcto_ref.item_orcamento
                else:
                    projeto = ''
                    orcamento = ''


            if field.name == 'data_lcto':
                value = value.strftime('%d/%m/%Y')
                
            if field.name not in ['id', 'tipo', 'valor']:
                data_row.append(f'{value}')
            if i == len(fields):
                data_row.append(f'{projeto}')
                data_row.append(f'{orcamento}')
                data_row.append(entrada)
                data_row.append(saida)
                data_row.append(saldo)
           
            for column, item in enumerate(data_row):
                worksheet.write(row + 2, column, item)
                linha = row +3

        worksheet.write(linha,0,"SALDO FINAL", bold_format)
        worksheet.write(linha,len(header_list)-1, saldo, bold_format)

    worksheet.set_column('A:A', 20)
    worksheet.set_column('B:B', 50)
    worksheet.set_column('C:C', 20)
    worksheet.set_column('D:D', 20)
    worksheet.set_column('E:E', 50)
    worksheet.set_column('F:K', 20)
    
    workbook.close()

    return response


"""
 



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


@admin.register(PagarReceber)
class PagarReceberAdmin(admin.ModelAdmin):
    inlines = [LctoDetalheInline,]
    def save_model(self, request, obj, form, change):
        usuario_logado = request.user
        obj.usuario = usuario_logado
        obj.save()


    list_display = ('data_vcto', 'descricao', )
    list_filter =(FiltroPagamentos, FiltroRecebimentos )
    readonly_fields = ['valor_pago', 'status', 'data_criacao', 'data_atualizacao', 'usuario']

@admin.register(MovimentosCaixa)
class MovimentoAdmin(admin.ModelAdmin):
    form = MovimentoFormAdmin
    #actions = [export_to_xlsx]
    def save_model(self, request, obj, form, change):
        usuario_logado = request.user
        obj.usuario = usuario_logado
        obj.save()

    list_per_page = 200
    list_display = ("__str__",)
    list_filter = (
        ContasFilter,'data_lcto', ('data_lcto', CustomDateRangeFilter), 
    )
    def get_changelist(self, request, **kwargs):
        return MyChangeList
    readonly_fields = ['data_criacao', 'data_atualizacao', 'usuario']
    class Media:
        js = ("jquery-3.6.3.min.js","form.js",)

#admin.site.register(MovimentosCaixa, MovimentoAdmin)
admin.site.register(ArquivosContabeis)

class ReciboInline(admin.TabularInline):
    model = ReciboDetalhe
    extra = 2


@admin.register(RecibosMaster)
class RecibosMasterAdmin(admin.ModelAdmin):
    inlines = [ReciboInline,]
    actions = [print_recibo]

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions