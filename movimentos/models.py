from django.db import models
from configuracoes.models import *
from django.contrib import admin
from django import forms

# Create your models here.


class ArquivosContabeis(models.Model):
      data = models.DateField(
              "Data do upload",
              auto_now=True,
              db_index=True
      )      
      descricao = models.CharField(
           "Descrição do Arquivo",
           max_length=50
      )
      TIPO_ARQUIVO = [
           ('NF', 'Nota Fiscal'),
           ('BL', 'Boleto'),
           ('CP', 'Comprovante'),
           ('EX', 'Extrato'),
           ('RC', 'Recibo'),
           ('OT', 'Outro')
      ]
      image = models.ImageField(
           "Arquivo a ser carregado",
           upload_to="documentos"
      )
      class Meta:
            ordering = ('data',)
            verbose_name = "Arquivo Suporte Contábil"
            verbose_name_plural = "Arquivos de Suporte Contábil"
      def __str__(self):
            return self.descricao



class PagarReceber(models.Model):
        data_lcto = models.DateField(
              "Data do Lançamento",
              auto_now=True,
              db_index=True
        )
        descricao = models.CharField(
             "Descrição do Lançamento",
             max_length=100
        )
        pessoa = models.ForeignKey(
            Pessoa,
            related_name='lcto_pess',
            on_delete=models.PROTECT,
            verbose_name="Pessoa",
        
        )
        data_vcto = models.DateField(
              "Data do Vencimento",
              db_index=True
        )

        especie = models.ForeignKey(
            Especie,
            related_name='lcto_especie',
            on_delete=models.PROTECT,
            verbose_name="Espécie do lançamento"
        )
        centro_custo = models.ForeignKey(
            CentrosCustos,
            related_name='lcto_cc',
            on_delete=models.PROTECT,
            verbose_name="Projeto"
        )
        item_orcamento = models.ForeignKey(
            ItensOrcamento,
            related_name='lcto_orc',
            on_delete=models.PROTECT,
            verbose_name="Item Orçamentário"
        )
        nro_docto = models.CharField(
              "Número do Documento",
              null=True,
              blank=True,
              max_length=25
        )
        valor_docto = models.DecimalField(
              max_digits=12,
              decimal_places=2
        )
        codigo_barras = models.CharField(
                "Código de Barras",
                null=True,
                blank=True,
                max_length=100
        )
        valor_pago = models.DecimalField(
              max_digits=12,
              decimal_places=2,
              default=0,
                          
        )

        STATUS_PGTO = [
              ('AB', 'Aberto'),
              ('PP', 'Parcialmente Pago'),
              ('TP', 'Totalmente Pago' ),
        ]

        status = models.CharField(
            "Status do Pagamento",
            max_length=2,
            choices= STATUS_PGTO,
            default='AB',
        )
        arquivo_suporte = models.ForeignKey(
            ArquivosContabeis,
            related_name='lcto_arq',
            on_delete=models.PROTECT,
            verbose_name="Arquivo de Suporte Contábil",
            null = True,
            blank = True
        )

        observacoes = models.TextField(
        null=True,
        blank=True,
        help_text="Notas ou comentários sobre este lançamento"
        )

        class Meta:
            ordering = ('data_vcto',)
            verbose_name = "Conta Pagar/Receber"
            verbose_name_plural = "Contas a Pagar/Receber"
        def __str__(self):
            return f"{self.descricao} vencimento {self.data_vcto.strftime('%d/%m/%Y')}"






class MovimentosCaixa(models.Model):
        TIPOS_MOVIMENTOS_CAIXA = [
            ('SI', 'Saldo Inicial'),
            ('TR', 'Transferência entre contas'),
            ('PG', 'Pagamento'),
            ('PR', 'Recebimento'),
            ('SP', 'Projetos - Saída para outro projeto'),
            ('EP', 'Projetos - Entrada de outro projeto')
        ]
        
        
        data_lcto = models.DateField(
            "Data da Movimentação",
            db_index=True
        )

        

        valor = models.DecimalField(
            "Valor",
            max_digits=12,
            decimal_places=2
        )
        
        tipo = models.CharField(
            "Tipo de movimento",
            max_length=2,
            choices= TIPOS_MOVIMENTOS_CAIXA,
            default='PG',
        )
        historico = models.CharField(
            "Histórico - descrição da movimentação",
            max_length=150
        )
        conta_origem = models.ForeignKey(
                Contas,
                models.SET_NULL,
                related_name='mov_conta_origem',
                null=True,
                blank=True,
                verbose_name="Conta de Origem",
                default = None
        )
        conta_destino = models.ForeignKey(
                Contas,
                models.SET_NULL,
                related_name='mov_conta_destino',
                null=True,
                blank=True,
                verbose_name="Conta de Destino",
                default = None
        )
        lcto_ref = models.ForeignKey(
                PagarReceber,
                models.SET_NULL,
                related_name='mov_lcto',
                null=True,
                blank=True,
                verbose_name="Lançamento de Referência"
        )

        arquivo_suporte = models.ForeignKey(
            ArquivosContabeis,
            related_name='mvto_arq',
            on_delete=models.PROTECT,
            verbose_name="Arquivo de Suporte Contábil",
            null = True,
            blank = True
        )
        class Meta:
            ordering = ('data_lcto', "id")
            verbose_name = "Movimentação de Caixa"
            verbose_name_plural = "Movimentações de Caixa"
            

        def __str__(self):
            return f"{self.historico} em {self.data_lcto.strftime('%d/%m/%Y')}"
        
class RecibosMaster(models.Model):
        data_rebibo = models.DateField('Data do Recibo', db_index=True)
        emitido = models.BooleanField(
              'Recibo Emitido', 
              default=False,
              null=True,
              blank=True)
        
        lancamento = models.ForeignKey(
              PagarReceber,
              related_name='lcto_recibo',
              on_delete=models.CASCADE,
              verbose_name="Lançamento de Referência",
              null = True,
              blank = True
        )

        forma_pagamento = models.TextField(
              "Forma de Pagamento",
              null=True, 
              blank=True)

        class Meta:
              ordering = ('-data_rebibo', )
              verbose_name = "Recibo"
              verbose_name_plural = "Recibos"

        def __str__(self):
                return f"Recibo de {self.lancamento.descricao} emitido em {self.data_rebibo.strftime('%d/%m/%Y')}"

class ReciboDetalhe(models.Model):
        recibo = models.ForeignKey(
              RecibosMaster,
              related_name='recibo_detalhe',
              on_delete=models.CASCADE,
              verbose_name="Recibo",
              null = True,
              blank = True
        )

        descricao = models.CharField('Descrição', max_length=150)
        periodo = models.CharField('Período', max_length=80)
        valor = models.DecimalField(
              max_digits=12,
              decimal_places=2
        )
        class Meta:
              ordering = ('recibo','descricao' )
              verbose_name = "Detalhe do Recibo"
              verbose_name_plural = "Detalhes do Recibo"

        def __str__(self):
                return f"Recibo de {self.recibo.lancamento.descricao} emitido em {self.recibo.data_rebibo.strftime('%d/%m/%Y')}"
      
        
        

