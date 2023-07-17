from datetime import datetime
from .models import *
from pessoas.models import *
from fpdf import FPDF
from django.http import HttpResponse
import tempfile
import zipfile
import shutil
import os

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
    pdf.cell(30, 8, 'SALDO INICIAL', 0, 0,'L')
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


    #pdf_bytes = pdf.output(dest='S').encode('latin1')
    #response = HttpResponse(pdf_bytes, content_type='application/pdf')
    #response['Content-Disposition'] = f'attachment; filename={conta}.pdf'





@admin.action(description='Imprimir Recibos')
def print_recibo(modeladmin, request, queryset):
    temp_dir = tempfile.mkdtemp()
    
    i = 0
    
    for item in queryset:
        itens = []    

        todos = item.recibo_detalhe.all()
        for t in todos:
            itens.append((t.descricao, t.periodo, t.valor))
        nome = item.lancamento.pessoa.nome  
        if(item.lancamento.pessoa.tipo == 'F'):
            tipo_desc = 'NOME'
            tipo_doc = 'CPF'
            documento = item.lancamento.pessoa.pessoasfisicas.cpf
        else:
            tipo_desc = 'RAZÃO SOCIAL'
            tipo_doc = 'CNPJ'
            documento = item.lancamento.pessoa.pessoasjuridicas.cnpj
            projeto = item.lancamento.centro_custo.descricao
        data = item.data_rebibo.strftime('%d/%m/%Y')
        forma_pagamento = item.forma_pagamento

        entradasaida = 'Entrada' 
        texto = ''
        if entradasaida == 'Entrada':
            texto = 'RECEBI DA ASSOCIAÇÃO DE DEFICIENTES VISUAIS E AMIGOS - ADEVA \n CNPJ: 50.599.638/0001-69'




        total = 0 
        conta = nome

        for item in itens:
            total += item[2]

        pdf = FPDF()
        
        pdf.add_page('P')
        
        pdf.set_font('Arial', '', 25)
        pdf.set_line_width(0.5)

        pdf.set_xy(80, 12)
    

        pdf.multi_cell(40, 20, 'RECIBO', 1, 'C', fill=False)
        pdf.ln(15)
        pdf.set_x(10)
        pdf.set_font('Arial', '', 14)
        
        pdf.cell(40, 12, tipo_desc, 1, 0,'C')
        pdf.cell(150, 12, nome, 1, 1,'L')
    #  pdf.multi_cell(40, 20, 'NOME', 1, 'C', fill=False)
        x = pdf.get_x()
        pdf.set_x(x)
    # pdf.multi_cell(150, 20, 'NOME', 1, 'L', fill=False)
        y = pdf.get_y()
        pdf.cell(40, 12,tipo_doc, 1, 0,'C')
        pdf.cell(150, 12, documento, 1, 1, 'L')
        pdf.cell(190, 12, 'PROJETO: '+ projeto, 1,1, 'C')
        pdf.multi_cell(190, 10, texto, 1,'C')
        pdf.cell(100, 12, 'DESCRIÇÃO', 1, 0, 'C')
        pdf.cell(50, 12, 'PERÍODO', 1, 0, 'C')
        pdf.cell(40, 12, 'VALOR', 1, 1, 'C')

        for item in itens:
            pdf.cell(100, 10, item[0], 1,0, 'L')
            pdf.cell(50, 10, item[1], 1,0, 'C')
            pdf.cell(40, 10, f"{item[2]:,.2f}".replace(',', '#').replace('.', ',').replace('#', '.'), 1, 1,'C')
        
        pdf.cell(150, 12, 'TOTAL', 1,0, 'L')
        pdf.cell(40, 12, f"{total:,.2f}".replace(',', '#').replace('.', ',').replace('#', '.'), 1,1, 'C')
        pdf.cell(40, 12, 'DATA', 1,0, 'C')
        pdf.cell(150, 12, data, 1,1, 'C')
        y = pdf.get_y()
        x = pdf.get_x()
        pdf.multi_cell(40, 10, 'FORMA DE \n PAGAMENTO ', 0, 'C', fill=False)
        
        pdf.set_xy(x+40,y)
        pdf.multi_cell(150, 8, forma_pagamento, 1, 'C')

        y_fim = pdf.get_y()

        pdf.rect(x,y,40, y_fim-y, 'D')

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
        file_names = [f for f in file_list if os.path.isfile(os.path.join(temp_dir, f))]
        with zipfile.ZipFile(zip_file_path, 'w') as zip_file:
            for c in file_names:
                pdf_file_path = f'{temp_dir}/{c}'
                zip_file.write(pdf_file_path, f'{c}')

        hoje = datetime.now().strftime('%d_%m_%Y')
        # Read the zip file data and send it as the response
        with open(zip_file_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename="recibos_{hoje}.zip"'

    # Cleanup: Delete the temporary directory and its contents
    shutil.rmtree(temp_dir)

    return response
        




#    pdf_bytes = pdf.output(dest='S').encode('latin1')
#    response = HttpResponse(pdf_bytes, content_type='application/pdf')
#    response['Content-Disposition'] = f'attachment; filename={conta}.pdf'


    