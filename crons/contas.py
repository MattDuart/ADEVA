import os
import sys
from django.core.mail import send_mail
from django.conf import settings
import xlsxwriter
from django.core.mail import EmailMessage
from django.utils import timezone
from datetime import date, timedelta


# Obtém o diretório do script atual
script_dir = os.path.dirname(os.path.abspath(__file__))

# Adiciona o diretório do projeto ao PYTHONPATH
sys.path.append(os.path.join(script_dir, '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adeva_project.settings')

# Agora você pode importar as configurações do Django
import django
django.setup()



from movimentos.models import PagarReceber

# Configuração do Django


def gerar_excel_pagamentos():
    # Obtém a data atual e a data limite (10 dias no futuro)
    data_atual = timezone.now().date() - timedelta(days=100)
    data_limite = data_atual + timedelta(days=100)
    
    # Filtra os pagamentos para os próximos dez dias
    pagamentos = PagarReceber.objects.filter(data_vcto__gte=data_atual, data_vcto__lte=data_limite)

    dataframe = []
    if len(pagamentos) == 0:
        print('Não há pagamentos selecionados para gerar o arquivo')
        return

    nome = 'Pagamentos_'+date.today().strftime('%d_%m_%Y')
    file_path = f'crons/{nome}.xlsx'

    workbook = xlsxwriter.Workbook(file_path, {'in_memory': True})
    bold_format = workbook.add_format({'bold': True})
    number_format = workbook.add_format()
    number_format.set_num_format("#,##0.00")
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
        data = item.data_lcto.strftime('%d/%m/%Y')
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

    # Envia o e-mail com o arquivo Excel como anexo
    send_mail_com_anexo(file_path)

    # Apaga o arquivo após enviar o e-mail
    os.remove(file_path)

def send_mail_com_anexo(file_path):
    # Crie um objeto EmailMessage
    email = EmailMessage(
        'Assunto do E-mail de Teste',
        'Este é um e-mail de teste enviado diretamente do shell do Django.',
        'notificacao@siga.adeva.org.br',
        ['matt@solonoi.org'],
    )

    print(file_path)

    # Adicione o arquivo Excel como anexo ao e-mail
    with open(file_path, 'rb') as file:
        email.attach('Nome_do_Arquivo.xlsx', file.read(), 'application/vnd.openxmlformats-officedocument.spreadsheet.sheet')
    
    email.send()

    


def send_emails():
    # Lógica para enviar e-mails
    send_mail(
        'Assunto do E-mail de Teste',
        'Este é um e-mail de teste enviado diretamente do shell do Django.',
        'notificacao@siga.adeva.org.br',
        ['matt@solonoi.org'],
    )

if __name__ == "__main__":
    gerar_excel_pagamentos()