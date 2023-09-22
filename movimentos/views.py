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
import os
import zipfile
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


class CustomPDF(FPDF):
    def __init__(self, cabecalho, conta, sizes, *args, **kwargs):
        # Call the constructor of the parent class
        super().__init__(*args, **kwargs)

        # Do something with arg1 and arg2
        self.cabecalho = cabecalho
        self.cabecalho[0] = 'Data'
        self.conta = conta
        self.size_cols = sizes

    def header(self):
        # Set the font and size for the header
        self.set_font('Arial', 'B', 12)
        # Set the header text
        self.cell(0, 8, 'ADEVA - Relatório de Caixa', align='C', ln=True)
        self.cell(0, 8, self.conta, align='C', ln=True)
        self.ln(2)
        x = self.get_x()  # Get current X position
        y = self.get_y()  # Get current Y position
        self.line(x, y, x + 280, y)
        self.set_font('Arial', 'B', 9)

        for k, col in enumerate(self.cabecalho):
            self.set_y(y)
            if k == len(self.cabecalho) - 1:
                self.set_x(x)
                self.multi_cell(self.size_cols[k], 5, col, align='L')
                x += self.size_cols[k]
            else:
                self.set_x(x)
                self.multi_cell(self.size_cols[k], 5, col, align='L')
                x += self.size_cols[k]

        self.ln(5)
        x = self.get_x()  # Get current X position
        y = self.get_y()  # Get current Y position
        self.line(x, y, x + 280, y)

    def footer(self):
        # Set the font and size for the footer
        self.set_font('Arial', 'I', 8)
        # Set the footer text
        self.set_y(-15)
        self.cell(0, 10, 'Página %s' % self.page_no(), 0, 0, 'C')


def gerar_excel(request):

    c_custo = request.POST.get('centro_custo', None)
    orcamento = request.POST.get('orcamento', None)
    conta = request.POST.get('conta', None)
    desc_custo = ''
    desc_orc = ''

    if c_custo != None and 'Todos' not in c_custo:
        desc_custo = 'Proj '+c_custo+' '
    if orcamento != None and 'Todos' not in orcamento:
        desc_orc = 'Item Orc '+orcamento+' '

    conta = conta if conta != None else 'Relatório Geral'
    if conta == 'all':
        conta = 'Relatório Geral'

    nome = conta+' '+desc_custo+desc_orc+' ' + \
        request.POST['mes']+'-'+request.POST['ano']

    content_disposition = f'attachment;filename={nome}.xlsx'
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheet.sheet')
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

    data_list = eval(request.POST['query'])

    for column, item in enumerate(header_list):
        worksheet.write(0, column, item, bold_format)

    contador = 1
    soma = Decimal(request.POST['soma'].replace(".", "").replace(",", "."))
    saldo = Decimal(request.POST['saldo'].replace(".", "").replace(",", "."))
    worksheet.write(1, 0, 'SALDO INICIAL', bold_format)
    worksheet.write(1, len(cabecalho)-1, soma, number_bold)

    contador += 1

    for linha in data_list:
        for k, col in enumerate(linha):
            if k >= len(cabecalho) - 3:
                col = Decimal(col.replace(".", "").replace(
                    ",", ".")) if col != '' else ''

                if k == len(cabecalho) - 1:
                    worksheet.write(contador, k, col, number_bold)
                else:
                    worksheet.write(contador, k, col, number_format)
            else:
                worksheet.write(contador, k, col)
        contador += 1

    worksheet.write(contador, 0, 'SALDO FINAL', bold_format)
    worksheet.write(contador, len(cabecalho)-1, saldo, number_bold)
    worksheet.set_column('A:A', 20)
    worksheet.set_column('B:B', 50)
    worksheet.set_column('C:C', 20)
    worksheet.set_column('D:D', 20)
    worksheet.set_column('E:E', 50)
    worksheet.set_column('F:K', 20)
    workbook.close()

    return response


class ReciboPDF(View):
    # Isso é necessário se você estiver desabilitando CSRF
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request):
        # Lógica para lidar com o método GET
        pass

    def post(self, request):
        # Lógica para lidar com o método POST
        return self.gerar_pdf(request)

    def gerar_pdf(self, request):

        c_custo = request.POST.get('centro_custo', None)
        orcamento = request.POST.get('orcamento', None)
        conta = request.POST.get('conta', None)

        desc_custo = ''
        desc_orc = ''
        if c_custo != None and 'Todos' not in c_custo:
            desc_custo = 'Proj '+c_custo+' '
        if orcamento != None and 'Todos' not in orcamento:
            desc_orc = 'Item Orc '+orcamento+' '
        conta = conta if conta != None else 'Relatório Geral'
        if conta == 'all':
            conta = 'Relatório Geral'

        nome = conta+' '+desc_custo+desc_orc+' ' + \
            request.POST['mes']+'-'+request.POST['ano']
        size_cols = [18, 50, 30, 30, 50, 25, 25, 18, 18, 18]
        contador = 0
        cabecalho = eval(request.POST['cabecalho'])

        pdf = CustomPDF(conta=nome, cabecalho=cabecalho, sizes=size_cols)

        pdf.add_page('L')
        pdf.set_auto_page_break(auto=True)

        pdf.set_font('Arial', '', 9)

        data_list = eval(request.POST['query'])
        pdf.cell(30, 8, 'SALDO INICIAL', 0, 0, 'L')
        pdf.set_x(274)
        pdf.cell(18, 8, request.POST['soma'], 0, 1, 'R')

        for linha in data_list:
            contador += 1
            for k, col in enumerate(linha):
                if k < len(cabecalho) - 3:
                    align = 'L'
                else:
                    align = 'R'

                if k == len(cabecalho) - 1:
                    pdf.cell(size_cols[k], 8, col, 0, 1, align)
                else:
                    pdf.cell(size_cols[k], 8, col, 0, 0, align)

        pdf.set_font('Arial', 'B', 9)
        pdf.cell(30, 8, 'SALDO FINAL', 0, 0, 'L')
        pdf.set_x(274)
        pdf.cell(18, 8, request.POST['saldo'], 0, 1, 'R')

        pdf_bytes = pdf.output(dest='S').encode('latin1')
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename={nome}.pdf'
        return response


def get_centro_custo_ou_orcamento_by_month_year(month, year, saldo_inicial=0, centro_custo='all', item_orcamento='all'):
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    array_final = []
    cabecalho = ['Data da Movimentação',
                 'Histórico da Movimentação',
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

    centro = []
    itens = []

    if centro_custo == 'all':
        c_custos = CentrosCustos.objects.all()
        for item in c_custos:
            centro.append(item.id)
    else:
        centro.append(centro_custo)

    if item_orcamento == 'all':
        i_orcamento = ItensOrcamento.objects.all()
        for item in i_orcamento:
            itens.append(item.id)
    else:
        itens.append(item_orcamento)

    retorno = MovimentosCaixa.objects.filter(Q(data_lcto__gte=start_date) & Q(data_lcto__lte=end_date) & Q(
        lcto_ref__centro_custo__id__in=centro) & Q(lcto_ref__item_orcamento__pk__in=itens)).exclude(Q(tipo='TR')).order_by('data_lcto')

    saldo = saldo_inicial

    for item in retorno:
        data_lancamento = item.data_lcto.strftime("%d/%m/%Y")
        historico = str(item.historico)
        origem = str(
            item.conta_origem) if item.conta_origem is not None else ''
        destino = str(
            item.conta_destino) if item.conta_destino is not None else ''
        if item.lcto_ref is not None:
            referencia = str(
                item.lcto_ref.descricao) if item.lcto_ref.descricao else ''
            projeto = str(
                item.lcto_ref.centro_custo) if item.lcto_ref.centro_custo else ''
            orcamento = str(
                item.lcto_ref.item_orcamento) if item.lcto_ref.item_orcamento else ''
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
        # não tem transferencia neste relatorio de centro de custos e orcamentos.
        elif item.tipo == 'TR':
            pass

        entrada = locale.format_string(
            '%.2f', entrada, grouping=True) if entrada != '' else ''
        saldo_formatado = locale.format_string(
            '%.2f', saldo, grouping=True) if saldo != '' else ''
        saida = locale.format_string(
            '%.2f', saida, grouping=True) if saida != '' else ''

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


def get_movimentos_caixa_by_month_year(month, year, account='all', saldo_inicial=0):
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    array_final = []
    cabecalho = ['Data da Movimentação',
                 'Histórico da Movimentação',
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

    if account == 'all':
        retorno = MovimentosCaixa.objects.filter(Q(data_lcto__gte=start_date) & Q(
            data_lcto__lte=end_date)).exclude(Q(tipo='TR')).order_by('data_lcto')
    else:
        retorno = MovimentosCaixa.objects.filter(Q(data_lcto__gte=start_date) & Q(data_lcto__lte=end_date) & (
            Q(conta_origem=account) | Q(conta_destino=account))).order_by('data_lcto')

    saldo = saldo_inicial

    for item in retorno:
        data_lancamento = item.data_lcto.strftime("%d/%m/%Y")
        historico = str(item.historico)
        origem = str(
            item.conta_origem) if item.conta_origem is not None else ''
        destino = str(
            item.conta_destino) if item.conta_destino is not None else ''
        if item.lcto_ref is not None:
            referencia = str(
                item.lcto_ref.descricao) if item.lcto_ref.descricao else ''
            projeto = str(
                item.lcto_ref.centro_custo) if item.lcto_ref.centro_custo else ''
            orcamento = str(
                item.lcto_ref.item_orcamento) if item.lcto_ref.item_orcamento else ''
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

        entrada = locale.format_string(
            '%.2f', entrada, grouping=True) if entrada != '' else ''
        saldo_formatado = locale.format_string(
            '%.2f', saldo, grouping=True) if saldo != '' else ''
        saida = locale.format_string(
            '%.2f', saida, grouping=True) if saida != '' else ''

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
    last_day_of_previous_month = datetime(
        year=year, month=month, day=1) - timedelta(days=1)

    # arrumar para sair entradas - saídas, e considerar (ou não) as transferencias
    tipos_de_entrada = ['PR', 'SI']
    tipos_de_saida = ['PG']

    if account == 'all':
        entradas = MovimentosCaixa.objects.filter(Q(data_lcto__lte=last_day_of_previous_month) & Q(
            tipo__in=tipos_de_entrada)).exclude(tipo='TR').aggregate(Sum('valor'))['valor__sum']
        saidas = MovimentosCaixa.objects.filter(Q(data_lcto__lte=last_day_of_previous_month) & Q(
            tipo__in=tipos_de_saida)).exclude(tipo='TR').aggregate(Sum('valor'))['valor__sum']

    else:
        entradas = MovimentosCaixa.objects.filter(Q(data_lcto__lte=last_day_of_previous_month) & Q(tipo__in=tipos_de_entrada) & (
            Q(conta_origem=account) | Q(conta_destino=account))).aggregate(Sum('valor'))['valor__sum']
        saidas = MovimentosCaixa.objects.filter(Q(data_lcto__lte=last_day_of_previous_month) & Q(tipo__in=tipos_de_saida) & (
            Q(conta_origem=account) | Q(conta_destino=account))).aggregate(Sum('valor'))['valor__sum']

    if entradas == None:
        entradas = 0
    if saidas == None:
        saidas = 0

    retorno = entradas - saidas

    return retorno


def get_centro_custo_sum_previous(month, year, centro_custo='all'):
    last_day_of_previous_month = datetime(
        year=year, month=month, day=1) - timedelta(days=1)

    # arrumar para sair entradas - saídas, e considerar (ou não) as transferencias
    tipos_de_entrada = ['PR', 'SI']
    tipos_de_saida = ['PG']

    if centro_custo == 'all':
        entradas = MovimentosCaixa.objects.filter(Q(data_lcto__lte=last_day_of_previous_month) & Q(
            tipo__in=tipos_de_entrada)).exclude(tipo='TR').aggregate(Sum('valor'))['valor__sum']
        saidas = MovimentosCaixa.objects.filter(Q(data_lcto__lte=last_day_of_previous_month) & Q(
            tipo__in=tipos_de_saida)).exclude(tipo='TR').aggregate(Sum('valor'))['valor__sum']

    else:
        entradas = MovimentosCaixa.objects.filter(Q(data_lcto__lte=last_day_of_previous_month) & Q(tipo__in=tipos_de_entrada) & Q(
            lcto_ref__centro_custo=centro_custo)).exclude(tipo='TR').aggregate(Sum('valor'))['valor__sum']
        saidas = MovimentosCaixa.objects.filter(Q(data_lcto__lte=last_day_of_previous_month) & Q(tipo__in=tipos_de_saida) & Q(
            lcto_ref__centro_custo=centro_custo)).exclude(tipo='TR').aggregate(Sum('valor'))['valor__sum']

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

    return render(request,
                  'movimento/lista.html',
                  {
                      'movimentos': movimentos,
                      'projetos': projetos,
                      'orcamentos': orcementos
                  })


def rel_detalhado(request):
    centros_custos = CentrosCustos.objects.all()
    orcamentos = ItensOrcamento.objects.all()
    context = admin.site.each_context(request)
    context['centros_custos'] = centros_custos
    context['orcamentos'] = orcamentos
    # Add custom context data here
    return render(request, 'relatorio_detalhado.html', context=context)


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

    soma = get_movimentos_caixa_sum_previous(
        int(request.POST['mes']), int(request.POST['ano']), conta_id)
    cabecalho, query, saldo = get_movimentos_caixa_by_month_year(
        int(request.POST['mes']), int(request.POST['ano']), conta_id, soma)

    my_context = {
        'mes': request.POST['mes'],
        'ano': request.POST['ano'],
        'conta': conta,
        'soma': soma,
        'query': query,
        'saldo': saldo,
        'cabecalho': cabecalho,

    }

    context = admin.site.each_context(request)
    context.update(my_context)

    return render(request, 'relatorio_fechamento.html', context)


def rel_final_detalhado(request):

    if request.POST['centro_custo'] == 'all':
        centro_custo_id = 'all'
        centro_custo = 'Todos os Projetos'
        soma = 0  # se for todos não é relevante o saldo total, pq em tese quer apenas os itens orçamentários
    else:
        centro_custo_id = request.POST['centro_custo']
        centro_custo = get_object_or_404(
            CentrosCustos, id=request.POST['centro_custo'])
        soma = get_centro_custo_sum_previous(
            int(request.POST['mes']), int(request.POST['ano']), centro_custo_id)
    if request.POST['orcamento'] == 'all':
        orcamento_id = 'all'
        orcamento = 'Todos os Itens Orçamentários'
    else:
        orcamento_id = request.POST['orcamento']
        orcamento = get_object_or_404(
            ItensOrcamento, id=request.POST['orcamento'])

    cabecalho, query, saldo = get_centro_custo_ou_orcamento_by_month_year(int(
        request.POST['mes']), int(request.POST['ano']), soma, centro_custo_id, orcamento_id)

    my_context = {
        'mes': request.POST['mes'],
        'ano': request.POST['ano'],
        'centro_custo': centro_custo,
        'orcamento': orcamento,
        'soma': f"{soma:,.2f}".replace(",", ".").replace(".", ",", 1),
        'query': query,
        'saldo': f"{saldo:,.2f}".replace(",", ".").replace(".", ",", 1),
        'cabecalho': cabecalho,

    }

    context = admin.site.each_context(request)
    context.update(my_context)

    return render(request, 'relatorio_final_detalhado.html', context)


# testar função abaixo que gera o arquivo zip com os documentos do mês
def view_download(request):
    # contas = Contas.objects.all()
    context = admin.site.each_context(request)
    # context['contas'] = contas
    # Add custom context data here
    return render(request, 'download_arquivos.html', context=context)


def download_documentos(request):
    month = int(request.POST['mes'])  # Obtém o valor do parâmetro 'mes' da URL
    year = int(request.POST['ano'])  # Obtém o valor do parâmetro 'ano' da URL

    last_day = calendar.monthrange(year, month)[1]
    start_date = datetime(year=year, month=month, day=1)
    end_date = datetime(year=year, month=month, day=last_day)

    retorno = MovimentosCaixa.objects.filter(Q(data_lcto__gte=start_date) & Q(
        data_lcto__lte=end_date)).exclude(Q(tipo='TR')).order_by('data_lcto')

    # Obtém a pasta 'documentos' no diretório raiz do seu projeto Django

    arquivos_filtrados = []
    caminho = os.path.normpath(os.path.join(os.getcwd(), 'media'))

    for item in retorno:
        # arquivos de titulos
        if item.lcto_ref.image:
            arquivo = os.path.normpath(os.path.join(
                caminho, str(item.lcto_ref.image)))
            arquivos_filtrados.append(arquivo)
        # arquivos de comprovantes
        if item.image:
            arquivo = os.path.normpath(os.path.join(caminho, str(item.image)))
            arquivos_filtrados.append(arquivo)

    # Cria um arquivo zip temporário para armazenar os documentos
    temp_zip_path = os.path.join(os.getcwd(), 'temp.zip')

    with zipfile.ZipFile(temp_zip_path, 'w') as zip_file:
        # Adiciona cada arquivo filtrado ao arquivo zip
        for arquivo in arquivos_filtrados:
            zip_file.write(arquivo, os.path.basename(arquivo))

    # Lê o conteúdo do arquivo zip como bytes
    with open(temp_zip_path, 'rb') as zip_file:
        zip_content = zip_file.read()

    # Deleta o arquivo zip temporário
    os.remove(temp_zip_path)

    # Cria uma resposta HTTP para o arquivo zip
    response = HttpResponse(zip_content, content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="documentos_{month}_{year}.zip"'

    return response
