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
    data_atual = date.today()
    dia_da_semana = data_atual.weekday()
    data_limite = data_atual + timedelta(days=10)


    arquivos = []
    corpo = ''
    relatorios = ['pagamentos_hoje','vencidos_nao_quitados',  'proximos_10_dias']
    for relatorio in relatorios:
        if relatorio == 'vencidos_nao_quitados':
            if dia_da_semana == 0:  #segunda-feira
                data = data_atual - timedelta(days=2)
            else:
                data = data_atual - timedelta(days=1)
            # Filtra os pagamentos vencidos
            pagamentos = PagarReceber.objects.filter(data_vcto__lt=data).filter(especie__tipo='O').exclude(status='TP')
            nome = relatorio+'_'+date.today().strftime('%d_%m_%Y')
            corpo += '\nVencidos e não quitados até ontem: \n'

        elif relatorio == 'pagamentos_hoje':
            # Filtra os pagamentos para hoje
            if dia_da_semana == 0:  #segunda-feira
                data = data_atual - timedelta(days=2)
                pagamentos = PagarReceber.objects.filter(data_vcto__gte=data, data_vcto__lte=data_atual).filter(especie__tipo='O').exclude(status='TP')
            else:
                pagamentos = PagarReceber.objects.filter(data_vcto=data_atual).filter(especie__tipo='O').exclude(status='TP')

            nome = relatorio+'_'+date.today().strftime('%d_%m_%Y')
            corpo += 'Pagamentos para hoje: \n'
        else:
            pagamentos = PagarReceber.objects.filter(data_vcto__gt=data_atual, data_vcto__lte=data_limite)
            nome = relatorio+'_'+date.today().strftime('%d_%m_%Y')
            corpo += '\nPróximos 10 dias: \n'

        dataframe = []
        if len(pagamentos) == 0:
            corpo += 'Nenhum pagamento encontrado para o período.\n'
            continue

        
        file_path = f'crons/{nome}.xlsx'

        arquivos.append(file_path)

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
        total = 0
        for item in pagamentos:
            data = item.data_lcto.strftime('%d/%m/%Y')
            descricao = item.descricao
            pessoa = item.pessoa.nome
            valor = item.valor_docto
            total += valor

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
        formatado = f"{total:,.2f}".replace(",", ";").replace(".", ",").replace(";", ".")

        if i == 1:
            tit = 'título'
        else:
            tit = 'títulos'

        corpo += f'Total: R$ {formatado} em {i} {tit} a pagar\n'

    # Envia o e-mail com o arquivo Excel como anexo

    if corpo != '':	
        corpo += '\n\nSeguem arquivos em anexo.' 
    else:
        corpo = 'Não há pagamentos para hoje, nem vencidos e não quitados até ontem, nem para os próximos 10 dias.'   

    send_mail_com_anexo(arquivos, corpo)

    # Apaga o arquivo após enviar o e-mail
    for file_path in arquivos:
       
        os.remove(file_path)

def send_mail_com_anexo(arquivos, corpo):
    # Crie um objeto EmailMessage
    email = EmailMessage(
        'SIGA - Notificação diária de pagamentos - EM TESTE', # tirar EM TESTE
        corpo,
        'notificacao@siga.adeva.org.br',
        ['markiano@adeva.org.br', 'sandra@adeva.org.br'],  # mudar para puxar de banco de dados
        bcc=['matt@solonoi.org']  # tirar
    )

 

    for file_path in arquivos:
    # Adicione o arquivo Excel como anexo ao e-mail
        with open(file_path, 'rb') as file:
            email.attach(os.path.basename(file_path), file.read(), 'application/vnd.openxmlformats-officedocument.spreadsheet.sheet')
        
    email.send()

    


if __name__ == "__main__":
    gerar_excel_pagamentos()