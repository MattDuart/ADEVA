# Create your views here.
from django.shortcuts import render, get_object_or_404
from .models import MovimentosCaixa, CentrosCustos, ItensOrcamento
from django.contrib import admin
from django.db.models import Q
from datetime import datetime, timedelta
from django.db.models import Sum
import calendar
from fpdf import FPDF
import xlsxwriter
from django.http import HttpResponse
from configuracoes.models import Contas

def gerar_excel(request):
    periodo = '03' + '05'
    content_disposition = f'attachment;filename=caixa_{periodo}.xlsx'
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheet.sheet')
    response['Content-Disposition'] = content_disposition
    workbook = xlsxwriter.Workbook(response, {'in_memory': True})
    worksheet = workbook.add_worksheet()
    header_list = []
    header_list.append("Projeto")
    header_list.append("Item Orçamentário")
    header_list.append("Entrada")
    header_list.append("Saída")
    header_list.append("Saldo")

    for column, item in enumerate(header_list):
        worksheet.write(0, column, item)

    workbook.close()

    return response





def gerar_pdf(request):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(40, 10, 'Hello World!')
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=tuto1.pdf'
    return response



def get_movimentos_caixa_by_month_year(month, year, account='all'):

    last_day = calendar.monthrange(year, month)[1]
    start_date = datetime(year=year, month=month, day=1)
    end_date = datetime(year=year, month=month, day=last_day)
    
    # arrumar para sair entradas - saídas, e considerar (ou não) as transferencias


    if account == 'all':
        retorno = MovimentosCaixa.objects.filter(Q(data_lcto__gte=start_date) & Q(data_lcto__lte=end_date)).exclude(Q(tipo='TR'))
    else:
        retorno = MovimentosCaixa.objects.filter(Q(data_lcto__gte=start_date) & Q(data_lcto__lte=end_date) & Q(conta_origem=account))       
    
    return retorno



def get_movimentos_caixa_sum_previous(month, year, account='all'):
    last_day_of_previous_month = datetime(year=year, month=month, day=1) - timedelta(days=1)

    # arrumar para sair entradas - saídas, e considerar (ou não) as transferencias
    tipos_de_entrada = ['PR', 'SI']
    tipos_de_saida = ['PG']

    if account == 'all':
        entradas = MovimentosCaixa.objects.filter(Q(data_lcto__lte=last_day_of_previous_month) & Q(tipo__in=tipos_de_entrada) ).exclude(tipo='TR').aggregate(Sum('valor'))['valor__sum']
        saidas = MovimentosCaixa.objects.filter(Q(data_lcto__lte=last_day_of_previous_month) & Q(tipo__in=tipos_de_saida)).exclude(tipo='TR').aggregate(Sum('valor'))['valor__sum']

        if entradas == None:
            entradas = 0
        if saidas == None:
            saidas = 0


        retorno = entradas - saidas

    return retorno




def movimentos_caixa_list(request):
    movimentos = MovimentosCaixa.objects.all()
    projetos = CentrosCustos.objects.all()
    orcementos = ItensOrcamento.objects.all()

    return render( request,
                  'movimento/lista.html',
                  {
                    'movimentos' : movimentos,
                    'projetos': projetos,
                    'orcamentos': orcementos
                  })


def fechamento_view(request):
    contas = Contas.objects.all()
    context = admin.site.each_context(request)
    context['contas'] = contas 
    # Add custom context data here
    return render(request, 'fechamento.html', context=context)

def rel_fechamento_view(request):
    if request.POST['conta'] == 'all':
        conta_id = 'all'
        conta['nome'] = 'Relatório Geral'
    else:
        conta_id = request.POST['conta']
        conta = get_object_or_404(Contas, id=request.POST['conta'])
    
    print('aqui')
    print(conta)

    #### só pra testar, tirar
    conta_id = 'all'
       

    query = get_movimentos_caixa_by_month_year(int(request.POST['mes']),int(request.POST['ano']), conta_id)
    
    print(query)
    soma = get_movimentos_caixa_sum_previous(int(request.POST['mes']),int(request.POST['ano']), conta_id)

    my_context = {
        'mes': request.POST['mes'],
        'ano': request.POST['ano'],
        'conta': conta,
        'soma': soma
    }

    context = admin.site.each_context(request)
    context.update(my_context)
   

    return render(request, 'relatorio_fechamento.html', context)

