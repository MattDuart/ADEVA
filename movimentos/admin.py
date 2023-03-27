from django.contrib import admin
from .forms import MovimentoFormAdmin
import datetime
import xlsxwriter
from django.http import HttpResponse
from django.db import models
from rangefilter.filters import DateRangeFilter, DateTimeRangeFilter, NumericRangeFilter
from django_filters import filters
from django_filters import ModelChoiceFilter
from django.db.models import Q
from django.utils import timezone
from django.http import QueryDict

# Register your models here.
from .models import PagarReceber, MovimentosCaixa, ArquivosContabeis
from configuracoes.models import Contas
from django.contrib.admin.filters import SimpleListFilter

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
    date_format = workbook.add_format({'num_format': 'dd/mm/YYYY'})

    fields = [field for field in opts.get_fields() \
               if not field.one_to_many and not isinstance(field, models.ForeignKey)]
    
    header_list = []
    for field in fields:
        if field.name not in ['id', 'tipo', 'valor']:
            header_list.append(f'{field.verbose_name}')

    header_list.append("Entrada")
    header_list.append("Saída")
    header_list.append("Saldo")
    
    movimentos = MovimentosCaixa.objects.all()
    
    for movimento in movimentos:
        for column, item in enumerate(header_list):
            worksheet.write(0, column, item)

        saldo = 0
        for row, obj in enumerate(queryset):
            data_row = []
            
            print(len(fields))
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
                        # fazer lógica
                        saida = ''
                        entrada = ''


                if field.name == 'data_lcto':
                    print(value)
                    value = value.strftime('%d/%m/%Y')
                    print(value)

                if field.name not in ['id', 'tipo', 'valor']:
                    data_row.append(f'{value}')
                if i == len(fields):
                    data_row.append(f'{entrada}')
                    data_row.append(f'{saida}')
                    data_row.append(f'{saldo}')
                print(data_row)
                for column, item in enumerate(data_row):
                    worksheet.write(row + 1, column, item)

    workbook.close()

    return response



 



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

class CustomDateRangeFilter(DateRangeFilter):
    def __init__(self, request, params, model, model_admin, *args, **kwargs):
      #  params_copy = QueryDict('', mutable=True)
      #  print(params)
      #  params_copy.update(params)
      #  print(params)
      #  params_copy.pop('data_lcto__gte', None)
      #   params_copy.pop('data_lcto__lt', None) 
     #   print(params_copy)
        super().__init__(request, params, model, model_admin, *args, **kwargs)


# Register your models here.
@admin.register(PagarReceber)
class PagarReceberAdmin(admin.ModelAdmin):
    list_display = ('data_vcto', 'descricao', )
    list_filter =(FiltroPagamentos, FiltroRecebimentos )

@admin.register(MovimentosCaixa)
class MovimentoAdmin(admin.ModelAdmin):
    form = MovimentoFormAdmin
    actions = [export_to_xlsx]
    list_filter = (
        ContasFilter,'data_lcto', ('data_lcto', CustomDateRangeFilter), 
    )
    class Media:
        js = ("jquery-3.6.3.min.js","form.js",)

#admin.site.register(MovimentosCaixa, MovimentoAdmin)
admin.site.register(ArquivosContabeis)