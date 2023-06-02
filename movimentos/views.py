# Create your views here.
from django.shortcuts import render, get_object_or_404
from django.core import serializers
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
import locale
from decimal import Decimal

class CustomPDF(FPDF):
    def header(self):
        # Set the font and size for the header
        self.set_font('Arial', 'B', 12)
        # Set the header text
        self.cell(0, 10, 'This is the header', align='C', ln=True)

    def footer(self):
        # Set the font and size for the footer
        self.set_font('Arial', 'I', 8)
        # Set the footer text
        self.cell(0, 10, 'Page %s' % self.page_no(), 0, 0, 'C')



def gerar_excel(request):
  

    conta = request.POST['conta'] if request.POST['conta'] != '' else 'Relatório Geral'
    nome = conta+' mês '+request.POST['mes']+'-'+request.POST['ano']
    content_disposition = f'attachment;filename={nome}.xlsx'
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheet.sheet')
    response['Content-Disposition'] = content_disposition
    workbook = xlsxwriter.Workbook(response, {'in_memory': True})
    bold_format = workbook.add_format({'bold': True})
    number_format = workbook.add_format()
    number_format.set_num_format("#,##0.00")

    number_bold = workbook.add_format({'bold': True})
    number_bold.set_num_format("#,##0.00")
   

    worksheet = workbook.add_worksheet()
    cabecalho = eval(request.POST['cabecalho'])
    header_list = []
    for coluna in cabecalho:
        header_list.append(coluna)


    print(len(cabecalho))

    data_list = eval(request.POST['query']) 


    for column, item in enumerate(header_list):
        worksheet.write(0, column, item, bold_format)

    contador = 1
    soma = Decimal(request.POST['soma'].replace(".", "").replace(",", "."))
    saldo = Decimal(request.POST['saldo'].replace(".", "").replace(",", "."))
    worksheet.write(1,0,'SALDO INICIAL', bold_format)
    worksheet.write(1,len(cabecalho)-1, soma, number_bold)
    
    contador += 1

    for linha in data_list:
        for k,col in enumerate(linha):
            if k >= len(cabecalho) -3 :  
                col = Decimal(col.replace(".", "").replace(",", ".")) if col != '' else  ''
                print(col)
                if k == len(cabecalho) -1:
                    worksheet.write(contador,k,col, number_bold)
                else:
                    worksheet.write(contador,k,col, number_format)
            else:    
                worksheet.write(contador,k,col)
        contador += 1 



    worksheet.write(contador,0,'SALDO FINAL', bold_format)
    worksheet.write(contador,len(cabecalho)-1, saldo, number_bold)

    worksheet.set_column('A:A', 20)
    worksheet.set_column('B:B', 50)
    worksheet.set_column('C:C', 20)
    worksheet.set_column('D:D', 20)
    worksheet.set_column('E:E', 50)
    worksheet.set_column('F:K', 20)

    workbook.close()

    return response





def gerar_pdf(request):
    
    conta = request.POST['conta'] if request.POST['conta'] != '' else 'Relatório Geral'
    nome = conta+' mês '+request.POST['mes']+'-'+request.POST['ano']

    size_cols = [15,40,20,20,40,15,15,15,15,15]


    pdf = CustomPDF()
    
    pdf.add_page()
    pdf.set_auto_page_break(auto=True)

    pdf.set_font('Arial', 'B', 16)


    data_list = eval(request.POST['query']) 

    for linha in data_list:
        for k,col in enumerate(linha):
            if k == len(request.POST['cabecalho']) - 1:
                pdf.cell(size_cols[k], 0, col, 1, 0,'C')
            else:
                pdf.cell(size_cols[k], 0, col, 0, 0,'C')

    pdf_bytes = pdf.output(dest='S').encode('latin1')
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename={conta}.pdf'
    return response



def get_movimentos_caixa_by_month_year(month, year, account='all', saldo_inicial=0):
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    array_final = []
    cabecalho = ['Data da Movimentação', 
                 'Histórico - descrição da movimentação',
                 'Conta de Origem',
                 'Conta de Destino',
                 'Lançamento de Referência',
                 'Projeto',
                 'Item Orçamentário',
                 'Entrada',
                 'Saída',
                 'Saldo']
    

    last_day = calendar.monthrange(year, month)[1]
    start_date = datetime(year=year, month=month, day=1)
    end_date = datetime(year=year, month=month, day=last_day)
    
    # arrumar para sair entradas - saídas, e considerar (ou não) as transferencias


    if account == 'all':
        retorno = MovimentosCaixa.objects.filter(Q(data_lcto__gte=start_date) & Q(data_lcto__lte=end_date)).exclude(Q(tipo='TR')).order_by('data_lcto')
    else:
        retorno = MovimentosCaixa.objects.filter(Q(data_lcto__gte=start_date) & Q(data_lcto__lte=end_date) & Q(conta_origem=account)).order_by('data_lcto')       
    


    saldo = saldo_inicial

    for item in retorno:
        data_lancamento = item.data_lcto.strftime("%d/%m/%Y")
        historico = str(item.historico)
        origem = str(item.conta_origem) if item.conta_origem is not None else ''
        destino = str(item.conta_destino) if item.conta_destino is not None else ''
        if item.lcto_ref is not None:
            referencia = str(item.lcto_ref.descricao) if item.lcto_ref.descricao else ''
            projeto = str(item.lcto_ref.centro_custo) if item.lcto_ref.centro_custo else '' 
            orcamento = str(item.lcto_ref.item_orcamento) if item.lcto_ref.item_orcamento else '' 
        else:
            referencia = ''
            projeto = ''
            orcamento = ''
        
        entrada = ''
        saida = ''

        if item.tipo == 'SI':
            entrada = item.valor
            saida = ''
            saldo += entrada
        elif item.tipo == 'PG':
            saida = item.valor
            entrada = ''
            saldo -= saida
        elif item.tipo == 'PR':
            entrada = item.valor
            saida = ''
            saldo += entrada
        elif item.tipo == 'TR':
            if item.conta_destino == account:
                entrada = item.valor
                saida = ''
                saldo += entrada
            if item.conta_origem == account:
                saida = item.valor
                entrada = ''
                saldo -= saida
    
    
        entrada = locale.format_string('%.2f', entrada, grouping=True) if entrada !=  '' else ''
        saldo_formatado = locale.format_string('%.2f', saldo, grouping=True) if saldo !=  '' else ''
        saida = locale.format_string('%.2f', saida, grouping=True) if saida !=  '' else ''


        linha = [data_lancamento,
                 historico,
                 origem,
                 destino,
                 referencia,
                 projeto,
                 orcamento,
                 entrada,
                 saida,
                 saldo_formatado]
        
        array_final.append(linha)

    

    return cabecalho, array_final, saldo



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
        conta = 'Relatório Geral'
    else:
        conta_id = request.POST['conta']
        conta = get_object_or_404(Contas, id=request.POST['conta'])
    
    print('aqui')
    print(conta)

    #### só pra testar, tirar
    conta_id = 'all'


    soma = get_movimentos_caixa_sum_previous(int(request.POST['mes']),int(request.POST['ano']), conta_id)


    cabecalho, query, saldo = get_movimentos_caixa_by_month_year(int(request.POST['mes']),int(request.POST['ano']), conta_id, soma)
    
    print(cabecalho)
    print(query)
    print(saldo)
    
    my_context = {
        'mes': request.POST['mes'],
        'ano': request.POST['ano'],
        'conta': conta,
        'soma': f"{soma:,.2f}".replace(",", ".").replace(".", ",", 1),
        'query': query,
        'saldo': saldo,
        'cabecalho': cabecalho,

    }

    context = admin.site.each_context(request)
    context.update(my_context)
   

    return render(request, 'relatorio_fechamento.html', context)

