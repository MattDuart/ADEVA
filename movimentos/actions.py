from .models import *
from fpdf import FPDF
from django.http import HttpResponse

def pdf_recibo_pagamento(nome=None, itens=None, id=None):
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
    
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename={conta}.pdf'





@admin.action(description='Imprimir Recibos')
def print_recibo(modeladmin, request, queryset):
    for item in queryset:
        print(queryset)
    
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
    
    pdf.add_page('P')
    
    pdf.set_font('Arial', '', 25)
    pdf.set_line_width(0.5)

    pdf.set_xy(80, 15)
   

    pdf.multi_cell(40, 20, 'RECIBO', 1, 'C', fill=False)
    pdf.ln(20)
    pdf.set_x(10)
    pdf.set_font('Arial', '', 14)
    y = pdf.get_y()
    x = pdf.get_x()
    pdf.set_xy(x,y)
    pdf.cell(40, 20, 'NOME', 1, 0,'C')
    pdf.cell(40, 20, 'NOME', 1, 1,'C')
  #  pdf.multi_cell(40, 20, 'NOME', 1, 'C', fill=False)
    x = pdf.get_x()
    pdf.set_x(x)
   # pdf.multi_cell(150, 20, 'NOME', 1, 'L', fill=False)
    y = pdf.get_y()
    pdf.multi_cell(40, 20, 'CPF', 1, 'C', fill=False)
    pdf.set_xy(x + 40,y)
    pdf.multi_cell(150, 20, 'NOME', 1, 'L', fill=False)
    pdf.multi_cell(190, 10, 'PROJETO', 1, 'C', fill=False)
    pdf.multi_cell(190, 20, 'Recebi de ....', 1, 'L', fill=False)
    y = pdf.get_y()
    x = pdf.get_x()
    pdf.set_xy(x,y)
    pdf.multi_cell(40, 20, 'DESCRIÇÃO', 1, 'C', fill=False)
    pdf.set_xy(x + 40,y)
    pdf.multi_cell(100, 20, 'PERÍODO', 1, 'C', fill=False)
    pdf.set_xy(x + 140,y)
    pdf.multi_cell(50, 20, 'VALOR', 1, 'C', fill=False)

    #aqui sao as linhas
    y = pdf.get_y()
    x = pdf.get_x()
    pdf.set_xy(x,y)
    pdf.multi_cell(40, 20, 'NOME', 1, 'C', fill=False)
    pdf.set_xy(x + 40,y)
    pdf.multi_cell(100, 20, 'NOME', 1, 'L', fill=False)
    pdf.set_xy(x + 140,y)
    pdf.multi_cell(50, 20, 'NOME', 1, 'C', fill=False)


    y = pdf.get_y()
    x = pdf.get_x()
    pdf.set_xy(x,y)
    pdf.multi_cell(140, 20, 'TOTAL', 1, 'C', fill=False)
    pdf.set_xy(x + 140,y)
    pdf.multi_cell(50, 20, 'NOME', 1, 'C', fill=False)


    y = pdf.get_y()
    x = pdf.get_x()
    pdf.set_xy(x,y)
    pdf.multi_cell(40, 20, 'DATA', 1, 'C', fill=False)
    pdf.set_xy(x + 40,y)
    pdf.multi_cell(150, 20, 'teste', 1, 'C', fill=False)
    y = pdf.get_y()
    pdf.multi_cell(40, 10, 'FORMA DE \n PAGAMENTO', 1, 'C', fill=False)
    pdf.set_xy(x + 40,y)
    pdf.multi_cell(150, 20, 'teste', 1, 'C', fill=False)

    pdf.ln(20)
    pdf.set_x(70)
    pdf.multi_cell(60, 10, 'PESSOA', 0, 'C', fill=False)
    pdf.set_x(70)
    pdf.multi_cell(60, 10, 'ASSINATURA', 0, 'C', fill=False)

    pdf_bytes = pdf.output(dest='S').encode('latin1')
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename={conta}.pdf'


    return response