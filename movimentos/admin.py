from django.contrib import admin
from .forms import MovimentoFormAdmin
import datetime
import xlsxwriter
from django.http import HttpResponse
from django.db import models

# Register your models here.
from .models import PagarReceber, MovimentosCaixa, ArquivosContabeis
from django.contrib.admin.filters import SimpleListFilter


def export_to_xlsx(modeladmin, request, queryset):
    opts = modeladmin.model._meta
    dateTimeObj = datetime.datetime.now()
    timestamp = dateTimeObj.strftime("%d-%b-%Y")
    content_disposition = f'attachment;filename=caixa_{timestamp}.xlsx'
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheet.sheet')
    response['Content-Disposition'] = content_disposition
    workbook = xlsxwriter.Workbook(response, {'in_memory': True})
    worksheet = workbook.add_worksheet()
    fields = [field for field in opts.get_fields() \
               if not field.one_to_many and not isinstance(field, models.ForeignKey)]
    header_list = [field.name for field in fields]
    movimentos = MovimentosCaixa.objects.all()
    for movimento in movimentos:
        header_list.append(f'{movimento.data_lcto}')
        header_list.append(f'{movimento.historico}')
        header_list.append(f'{movimento.valor}')

        for column, item in enumerate(header_list):
            worksheet.write(0, column, item)

        for row, obj in enumerate(queryset):
            data_row = []
            total = 0

            for field in fields:
                value = getattr(obj, field.name)
                if field.name == 'valor':
                    total += value
                if isinstance(value, datetime.datetime):
                    value = value.strftime('%d %m %Y')
                data_row.append(value)

                for column, item in enumerate(data_row):
                    worksheet.write(row + 1, column, item)

    workbook.close()

    return response
export_to_xlsx.shortdescription ='Exportar para Excel'        










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








# Register your models here.
@admin.register(PagarReceber)
class PagarReceberAdmin(admin.ModelAdmin):
    list_display = ('data_vcto', 'descricao', )
    list_filter =(FiltroPagamentos, FiltroRecebimentos )

@admin.register(MovimentosCaixa)
class MovimentoAdmin(admin.ModelAdmin):
    form = MovimentoFormAdmin
    actions = [export_to_xlsx]
    list_filter = ('data_lcto',)
    class Media:
        js = ("jquery-3.6.3.min.js","form.js",)

#admin.site.register(MovimentosCaixa, MovimentoAdmin)
admin.site.register(ArquivosContabeis)