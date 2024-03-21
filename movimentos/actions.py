from datetime import datetime, date
from .models import *
from pessoas.models import *
from fpdf import FPDF
from django.http import HttpResponse
import tempfile
import zipfile
import shutil
import os
import xlsxwriter
import mimetypes


def count_files_in_temporary_folder(temp_dir):

    # List all files in the temporary directory
    file_list = os.listdir(temp_dir)

    # Filter out directories from the file list
    files = [f for f in file_list if os.path.isfile(os.path.join(temp_dir, f))]

    # Get the count of files
    file_count = len(files)

    return file_count


def pdf_recibo_pagamento(nome=None, itens=None, id=None):
    temp_dir = tempfile.mkdtemp()
    i = 0

    print('PDF RECIBO PAGAMENTO')
    itens = [('Pagamento teste 1', 100.00), ('Pagamento teste 2', 200.00)]
    nome = 'Teste'
    documento = '039.359.686-98'
    data = '01/01/2020'
    projeto = 'Gráfica'
    entradasaida = 'Entrada'
    forma_pagamento = 'Dinheiro'
    total = 0
    conta = nome

    for item in itens:
        total += item[1]

    pdf = FPDF()

    pdf.add_page('L')

    pdf.set_font('Arial', '', 9)
    pdf.cell(30, 8, 'SALDO INICIAL', 0, 0, 'L')
    pdf.set_x(274)

    pdf_file_path = f'{temp_dir}/{conta}.pdf'
    i += 1

    pdf.output(pdf_file_path)

    zip_file_path = f'{temp_dir}/pdfs.zip'
    with zipfile.ZipFile(zip_file_path, 'w') as zip_file:
        for i in range(3):
            pdf_file_path = f'{temp_dir}/pdf{i+1}.pdf'
            zip_file.write(pdf_file_path, f'pdf{i+1}.pdf')

    # Read the zip file data and send it as the response
    with open(zip_file_path, 'rb') as file:
        response = HttpResponse(file.read(), content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="pdfs.zip"'

    # Cleanup: Delete the temporary directory and its contents
    shutil.rmtree(temp_dir)

    return response

    # pdf_bytes = pdf.output(dest='S').encode('latin1')
    # response = HttpResponse(pdf_bytes, content_type='application/pdf')
    # response['Content-Disposition'] = f'attachment; filename={conta}.pdf'




@admin.action(description='Imprimir Lista com selecionados')
def print_selected(modeladmin, request, queryset):
    pdf = FPDF()

    pdf.add_page('L')

    pdf.set_font('Arial', '', 9)

    pdf.cell(20, 8, 'Data Vcto', 1, 0, 'C')
    pdf.cell(70, 8, 'Pessoa', 1, 0, 'C')
    pdf.cell(70, 8, 'Descrição', 1, 0, 'C')
    pdf.cell(30, 8, 'Valor', 1, 0, 'C')
    pdf.cell(25, 8, 'Especie', 1, 0, 'C')
    pdf.cell(30, 8, 'Valor Pago', 1, 0, 'C')
    pdf.cell(30, 8, 'Conta', 1, 1, 'C')

    for item in queryset:
        pdf.cell(20, 8, item.data_vcto.strftime('%d/%m/%Y'), 1, 0, 'C')
        pdf.cell(70, 8, item.pessoa.nome[0:30], 1, 0, 'C')
        pdf.cell(70, 8, item.descricao[0:30], 1, 0, 'C')
        pdf.cell(30, 8, f"{item.valor_docto:,.2f}".replace(
            ',', '#').replace('.', ',').replace('#', '.'), 1, 0, 'C')
        pdf.cell(25, 8, item.especie.descricao[0:11], 1, 0, 'C')
        pdf.cell(30, 8, f"{item.valor_pago:,.2f}".replace(
            ',', '#').replace('.', ',').replace('#', '.'), 1, 0, 'C')
        
        if item.valor_pago == 0:
            conta = 'EM ABERTO'
        else:
            conta = MovimentosCaixa.objects.filter(lcto_ref=item).first()
            if conta is not None:

                if conta.conta_origem is not None:
                    conta = conta.conta_origem.nome[0:14]
                else:
                    conta = conta.conta_destino.nome[0:14]
            

        pdf.cell(30, 8, conta, 1, 1, 'C')


    temp_dir = tempfile.mkdtemp()

    pdf_file_path = f'{temp_dir}/lista.pdf'

    pdf.output(pdf_file_path)

    with open(pdf_file_path, 'rb') as file:
        response = HttpResponse(file.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="lista.pdf"'

    shutil.rmtree(temp_dir)

    return response


    








@admin.action(description='Imprimir Recibos')
def print_recibo_lcto(modeladmin, request, queryset):
    temp_dir = tempfile.mkdtemp()

    i = 0

    for item in queryset:
        itens = []

        todos = item.lcto_detalhe.all()
        if len(todos) == 0:
            itens.append((item.descricao, '', item.valor_docto))
        else:
            for t in todos:
                itens.append((t.descricao, t.periodo_qtde, t.valor))
        nome = item.pessoa.nome
        if (item.pessoa.tipo == 'F'):
            tipo_desc = 'NOME'
            tipo_doc = 'CPF'
            documento = item.pessoa.pessoasfisicas.cpf
            projeto = item.centro_custo.descricao
        else:
            tipo_desc = 'RAZÃO SOCIAL'
            tipo_doc = 'CNPJ'
            documento = item.pessoa.pessoasjuridicas.cnpj
            projeto = item.centro_custo.descricao

        recibo = RecibosMaster.objects.filter(lancamento=item)
        if len(recibo) > 0:
            data = recibo[0].data_recibo.strftime('%d/%m/%Y')
            numero = recibo[0].pk
        else:
            data = date.today()
            novo_recibo = RecibosMaster(lancamento=item, data_recibo=data)
            data = data.strftime('%d/%m/%Y')
            novo_recibo.save()
            numero = novo_recibo.pk

        print(numero)

        # verificar se já existe recibo

        f_pagamento = item.forma_pgto
        FORMAS_PGTO = [
            ('BL', 'BOLETO'),
            ('TR', 'TRANSFERÊNCIA'),
            ('ES', 'ESPÉCIE'),
            ('OU', 'OUTRO')
        ]
        forma_pagamento = ''
        for f in FORMAS_PGTO:
            if f[0] == f_pagamento:
                forma_pagamento = f[1]

        detalhes_pgto = None

        if item.conta_pgto is not None:
            if item.conta_pgto.numero_banco is not None or item.conta_pgto.nome_banco is not None:
                banco = f'\n BANCO: {item.conta_pgto.numero_banco} - {item.conta_pgto.nome_banco}'
            else:
                banco = ''

            if item.conta_pgto.documento is not None:
                favorecido = f'\n FAVORECIDO: {item.conta_pgto.favorecido} \n CPF/CNPJ: {item.conta_pgto.documento}'
            else:
                favorecido = ''

            if item.conta_pgto.numero_agencia is not None:
                dados = f'\n AGÊNCIA: {item.conta_pgto.numero_agencia} - {item.conta_pgto.digito_agencia} CONTA: {item.conta_pgto.numero_conta} - {item.conta_pgto.digito_conta}'
            else:
                dados = ''

            if item.conta_pgto.chave_pix is not None:
                TIPOS_PIX = [
                    ('D', 'CPF/CNPJ'),
                    ('T', 'Celular'),
                    ('E', 'Email'),
                    ('B', 'Agência e Conta'),
                    ('A', 'Chave Aleatória'),

                ]
                for j in TIPOS_PIX:
                    if j[0] == item.conta_pgto.tipo:
                        tipo_pix = j[1]
                        break

                pix = f'\n CHAVE PIX: {item.conta_pgto.chave_pix} -  Tipo: {tipo_pix}'

            else:
                pix = ''

            detalhes_pgto = banco
            forma_pagamento = forma_pagamento + banco + favorecido + dados + pix

        entradasaida = 'Entrada'
        texto = ''
        if item.especie.tipo == 'O':
            texto = 'RECEBI DA ASSOCIAÇÃO DE DEFICIENTES VISUAIS E AMIGOS - ADEVA \n CNPJ: 50.599.638/0001-69'
        else:
            texto = 'RECEBI DE ' + item.pessoa.nome + '\n DOC. Nro: ' + documento
            nome = 'ASSOCIAÇÃO DE DEFICIENTES VISUAIS E AMIGOS - ADEVA'
            documento = '50.599.638/0001-69'

        total = 0
        conta = nome

        for item in itens:
            total += item[2]

        pdf = FPDF()

        pdf.add_page('P')

        pdf.set_font('Arial', '', 25)
        pdf.set_line_width(0.5)

        pdf.set_xy(80, 12)

        pdf.multi_cell(40, 20, 'RECIBO', 0, 'C', fill=False)
        pdf.set_xy(140, 12)
        pdf.cell(40, 20, 'Nro:' + str(numero), 0, 0, 'C')
        pdf.ln(25)
        pdf.set_x(10)

        pdf.set_font('Arial', '', 14)

        pdf.cell(40, 12, tipo_desc, 1, 0, 'C')
        pdf.cell(150, 12, nome, 1, 1, 'L')
    #  pdf.multi_cell(40, 20, 'NOME', 1, 'C', fill=False)
        x = pdf.get_x()
        pdf.set_x(x)
    # pdf.multi_cell(150, 20, 'NOME', 1, 'L', fill=False)
        y = pdf.get_y()
        pdf.cell(40, 12, tipo_doc, 1, 0, 'C')
        pdf.cell(150, 12, documento, 1, 1, 'L')
        pdf.cell(190, 12, 'PROJETO: ' + projeto, 1, 1, 'C')
        pdf.multi_cell(190, 10, texto, 1, 'C')
        pdf.cell(100, 12, 'DESCRIÇÃO', 1, 0, 'C')
        pdf.cell(50, 12, 'PERÍODO', 1, 0, 'C')
        pdf.cell(40, 12, 'VALOR', 1, 1, 'C')

        for item in itens:
            pdf.cell(100, 10, item[0], 1, 0, 'L')
            pdf.cell(50, 10, item[1], 1, 0, 'C')
            pdf.cell(40, 10, f"{item[2]:,.2f}".replace(
                ',', '#').replace('.', ',').replace('#', '.'), 1, 1, 'C')

        pdf.cell(150, 12, 'TOTAL', 1, 0, 'L')
        pdf.cell(40, 12, f"{total:,.2f}".replace(',', '#').replace(
            '.', ',').replace('#', '.'), 1, 1, 'C')
        pdf.cell(40, 12, 'DATA', 1, 0, 'C')
        pdf.cell(150, 12, data, 1, 1, 'C')
        y = pdf.get_y()
        x = pdf.get_x()
        pdf.multi_cell(40, 8, 'FORMA DE \n PAGAMENTO ', 0, 'C', fill=False)

        pdf.set_xy(x+40, y)

        if detalhes_pgto is None:
            pdf.multi_cell(150, 16, forma_pagamento, 1, 'C')
        else:
            pdf.multi_cell(150, 8, forma_pagamento, 1, 'C')

        y_fim = pdf.get_y()

        pdf.rect(x, y, 40, y_fim-y, 'D')

        pdf.ln(15)
        pdf.set_x(40)
        pdf.multi_cell(120, 8, nome, 0, 'C')
        pdf.set_x(70)
        pdf.multi_cell(60, 8, 'Assinatura', 0, 'C', fill=False)
        pdf_file_path = f'{temp_dir}/{conta}.pdf'
        pdf.output(pdf_file_path)
        i += 1

    zip_file_path = f'{temp_dir}/recibos.zip'

    number_files = count_files_in_temporary_folder(temp_dir)

    if number_files == 1:
        pdf_bytes = pdf.output(dest='S').encode('latin1')
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename={conta}.pdf'

    else:
        file_list = os.listdir(temp_dir)

        # Filter out directories from the file list
        file_names = [f for f in file_list if os.path.isfile(
            os.path.join(temp_dir, f))]
        with zipfile.ZipFile(zip_file_path, 'w') as zip_file:
            for c in file_names:
                pdf_file_path = f'{temp_dir}/{c}'
                zip_file.write(pdf_file_path, f'{c}')

        hoje = datetime.now().strftime('%d_%m_%Y')
        # Read the zip file data and send it as the response
        with open(zip_file_path, 'rb') as file:
            response = HttpResponse(
                file.read(), content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename="recibos_{hoje}.zip"'

    # Cleanup: Delete the temporary directory and its contents
    shutil.rmtree(temp_dir)

    return response


#    pdf_bytes = pdf.output(dest='S').encode('latin1')
#    response = HttpResponse(pdf_bytes, content_type='application/pdf')
#    response['Content-Disposition'] = f'attachment; filename={conta}.pdf'


@admin.action(description='Gerar Excel Pagamentos')
def gerar_excel_pagamentos(modeladmin, request, queryset):
    pagamentos = queryset.filter(especie__tipo='O').exclude(status='TP')

    dataframe = []

    if len(pagamentos) == 0:
        return HttpResponse('Não há pagamentos selecionados para gerar o arquivo')

    nome = 'Pagamentos_'+date.today().strftime('%d_%m_%Y')
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

    cabecalho = [
        'Data Vencimento',
        'Descrição',
        'Pessoa',
        'Valor',
        'Forma de Pagamento',
        'Projeto',
        'Item Orçamentário',
        'Nº Documento',
        'Código de Barras',
        'Favorecido',
        'CPF/CNPJ',
        'Número Banco',
        'Nome Banco',
        'Número Agência',
        'Agência',
        'Número Conta',
        'Dígito Conta',
        'Chave Pix',
        'Tipo'
    ]

    dataframe.append(cabecalho)

    for column, item in enumerate(cabecalho):
        worksheet.write(0, column, item, bold_format)

    i = 0
    for item in pagamentos:
        data = item.data_vcto.strftime('%d/%m/%Y')
        descricao = item.descricao
        pessoa = item.pessoa.nome
        valor = item.valor_docto

        if item.forma_pgto == 'BL':
            forma_pgto = 'BOLETO'
        elif item.forma_pgto == 'TR':
            forma_pgto = 'TRANSFERÊNCIA'
        elif item.forma_pgto == 'ES':
            forma_pgto = 'ESPÉCIE'
        else:
            forma_pgto = 'OUTRO'

        projeto = item.centro_custo.descricao
        item_orcamento = item.item_orcamento.descricao
        nro_docto = item.nro_docto
        codigo_barra = item.codigo_barras

        if item.conta_pgto is not None:
            numero_banco = item.conta_pgto.numero_banco
            nome_banco = item.conta_pgto.nome_banco
            numero_agencia = item.conta_pgto.numero_agencia
            agencia = item.conta_pgto.digito_agencia
            numero_conta = item.conta_pgto.numero_conta
            digito_conta = item.conta_pgto.digito_conta
            chave_pix = item.conta_pgto.chave_pix
            tipo = item.conta_pgto.tipo
            favorecido = item.conta_pgto.favorecido
            documento = item.conta_pgto.documento

            if tipo == 'D':
                tipo = 'CPF/CNPJ'
            elif tipo == 'T':
                tipo = 'Celular'
            elif tipo == 'E':
                tipo = 'Email'
            elif tipo == 'B':
                tipo = 'Agência e Conta'
            else:
                tipo = 'Chave Aleatória'

        else:
            numero_banco = ''
            nome_banco = ''
            numero_agencia = ''
            agencia = ''
            numero_conta = ''
            digito_conta = ''
            chave_pix = ''
            tipo = ''
            favorecido = ''
            documento = ''

        linha = [data, descricao, pessoa, valor, forma_pgto, projeto, item_orcamento, nro_docto, codigo_barra, favorecido,
                 documento, numero_banco, nome_banco, numero_agencia, agencia, numero_conta, digito_conta, chave_pix, tipo]
        dataframe.append(linha)
        i += 1
        for column, item in enumerate(linha):
            if column == 3:
                worksheet.write(i, column, item, number_format)
            else:
                worksheet.write(i, column, item)

    for col_num, col_data in enumerate(zip(*dataframe)):
        max_length = max(len(str(cell)) for cell in col_data)
        worksheet.set_column(col_num, col_num, max_length + 2)

    workbook.close()

    return response


@admin.action(description='Fazer download do arquivo (boletos ou comprovantes)')
def download_doc(modeladmin, request, queryset):

    retorno = queryset
    # Obtém a pasta 'documentos' no diretório raiz do seu projeto Django

    arquivos_filtrados = []
    caminho = os.path.normpath(settings.MEDIA_ROOT)

    for item in retorno:

        if item.image:
            arquivo = os.path.normpath(os.path.join(caminho, str(item.image)))
            arquivos_filtrados.append(arquivo)

    if len(arquivos_filtrados) == 1:
        primeiro_arquivo = arquivos_filtrados[0]

        print(primeiro_arquivo)
        nome_arquivo = os.path.basename(primeiro_arquivo)
        print(nome_arquivo)

        tipo_conteudo, _ = mimetypes.guess_type(nome_arquivo)

    # Lê o conteúdo do arquivo em modo binário
        with open(primeiro_arquivo, 'rb') as arquivo:
            response = HttpResponse(arquivo.read(), content_type=tipo_conteudo)

            # Define o cabeçalho Content-Disposition para forçar o download
            response['Content-Disposition'] = f'attachment; filename="{nome_arquivo}"'

            return response
    else:

        # Cria um arquivo zip temporário para armazenar os documentos
        temp_zip_path = os.path.join(settings.MEDIA_ROOT, 'temp.zip')

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
        response['Content-Disposition'] = f'attachment; filename="documentos.zip"'

        return response
