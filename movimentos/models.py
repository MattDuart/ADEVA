from django.db import models
from configuracoes.models import *
from pessoas.models import Pessoa, DadosPgto
from django.contrib import admin
from django import forms
from django.contrib.auth.models import User
from django.utils import timezone
import os
import unicodedata
from django.conf import settings
import random


def sanitize_filename(filename):
    # Substituir espaços por underscores
    filename = filename.replace(' ', '_')

    # Remover acentos e caracteres especiais
    filename = unicodedata.normalize('NFKD', filename).encode(
        'ASCII', 'ignore').decode('utf-8')

    # Limitar o tamanho do nome do arquivo a 220 caracteres
    filename = filename[:220]

    return filename


# Create your models here.

def upload_to_lancamentos(instance, filename):
    # instance.save()
    # Gere um novo nome de arquivo para evitar conflitos
    if hasattr(instance, 'data_vcto'):
        mes = instance.data_vcto.strftime("%m")
        ano = instance.data_vcto.strftime("%Y")
        dia = instance.data_vcto.strftime("%d")
        descricao = instance.descricao[0:40].replace('/', '_')
    else:
        mes = instance.lcto.data_vcto.strftime("%m")
        ano = instance.lcto.data_vcto.strftime("%Y")
        dia = instance.lcto.data_vcto.strftime("%d")
        descricao = instance.lcto.descricao[0:40].replace('/', '_')

    if (instance.pk is None):
        id = 0
    else:
        id = int(instance.pk)

    numero_aleatorio = random.randint(0, 2**32 - 1)

# Converter para hexadecimal
    numero_hex = format(numero_aleatorio, 'x')

    name_without_extension, extension = os.path.splitext(filename)
    arquivo = sanitize_filename(dia+'_'+mes+'_'+ano+'_'+descricao+'_'+numero_hex).replace('/', '_')
    new_filename = f"doc_{arquivo}{extension}"
    # Construa o caminho completo para upload
    return os.path.join("lancamentos", str(ano), str(mes), new_filename)


def upload_to_movimentos(instance, filename):
    # instance.save()
    # Gere um novo nome de arquivo para evitar conflitos
    mes = instance.data_lcto.strftime("%m")
    ano = instance.data_lcto.strftime("%Y")
    dia = instance.data_lcto.strftime("%d")
    

    name_without_extension, extension = os.path.splitext(filename)
    arquivo = sanitize_filename(dia+'_'+mes+'_'+ano+'_'+instance.historico[0:40]).replace('/', '_')
    new_filename = f"compr_{arquivo}{extension}"

    # Construa o caminho completo para upload
    return os.path.join("movimentos", str(ano), str(mes), new_filename)


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

    tipo_documento = models.ForeignKey(
        TiposDocumentos,
        related_name='lcto_tipo_doc',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Tipo de Documento"
    )


    valor_docto = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    FORMAS_PGTO = [
        ('BL', 'BOLETO'),
        ('TR', 'TRANSFERÊNCIA'),
        ('ES', 'ESPÉCIE'),
        ('OU', 'OUTRO')
    ]

    forma_pgto = models.CharField("Forma de Pagamento(se houver)",
                                  max_length=2,
                                  choices=FORMAS_PGTO,
                                  blank=True,
                                  null=True,
                                  default=None,
                                  )

    codigo_barras = models.CharField(
        "Código de Barras (se houver)",
        null=True,
        blank=True,
        max_length=100
    )
    conta_pgto = models.ForeignKey(
        DadosPgto,
        related_name='lcto_conta_pgto',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,

        verbose_name="Conta para pagamento(se houver)"
    )

    valor_pago = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,

    )

    STATUS_PGTO = [
        ('AB', 'Aberto'),
        ('PP', 'Parcialmente Pago'),
        ('TP', 'Totalmente Pago'),
    ]

    status = models.CharField(
        "Status do Pagamento",
        max_length=2,
        choices=STATUS_PGTO,
        default='AB',
    )

    image = models.FileField(
        "Arquivo a ser carregado",
        upload_to=upload_to_lancamentos,
        null=True,
        blank=True
    )

    
    data_limite_emissao_nota = models.DateField(
        "Data limite para emissão de nota fiscal (quando aplicável)",
        null=True,
        blank=True,
        help_text="Data limite para emissão de nota fiscal em casos de MEI ou outros casos específicos"
    )


    obs_emissao_notas = models.TextField(
        null=True,
        blank=True,
        help_text="Dados para orientação de emissão de nota fiscal",
        verbose_name="Descriçao para emissão de notas fiscais (quando aplicável)"
    )

    observacoes = models.TextField(
        null=True,
        blank=True,
        help_text="Notas ou comentários sobre este lançamento"
    )

    data_criacao = models.DateTimeField(
        auto_now_add=True, verbose_name="Data de Criação do Lançamento")
    data_atualizacao = models.DateTimeField(
        auto_now=True, verbose_name="Data de Atualização do Lançamento")
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL,
                                null=True, verbose_name="Usuário responsável pelo Lançamento")

    class Meta:
        ordering = ('-data_vcto',)
        verbose_name = "Conta Pagar/Receber"
        verbose_name_plural = "Contas a Pagar/Receber"

    def __str__(self):
        return f"{self.descricao} vencimento {self.data_vcto.strftime('%d/%m/%Y')}"


class LctoDetalhe(models.Model):
    lcto = models.ForeignKey(
        PagarReceber,
        related_name='lcto_detalhe',
        on_delete=models.CASCADE,
        verbose_name="Recibo",
        null=True,
        blank=True
    )


    descricao = models.CharField(
        'Descrição do produto/serviço', max_length=150)
    periodo_qtde = models.CharField('Período/Quantidade', max_length=80)
    valor = models.DecimalField(
        'Valor total do item',
        max_digits=12,
        decimal_places=2
    )

    centro_custo = models.ForeignKey(
        CentrosCustos,
        related_name='lcto_det_cc',
        on_delete=models.SET_NULL,
        verbose_name="Projeto",
        blank=True,
        null=True
    )
    item_orcamento = models.ForeignKey(
        ItensOrcamento,
        related_name='lcto_det_orc',
        on_delete=models.SET_NULL,
        verbose_name="Item Orçamentário",
        blank=True,
        null=True
    )

    class Meta:
        ordering = ('lcto', 'descricao')
        verbose_name = "Item do Lançamento"
        verbose_name_plural = "Itens do Lançamento"

    def __str__(self):
        return f"Detalhes de {self.lcto.descricao} de {self.lcto.data_vcto.strftime('%d/%m/%Y')}"
    

class OutrosArquivosLcto(models.Model):
    lcto = models.ForeignKey(
        PagarReceber,
        related_name='lcto_arquivos',
        on_delete=models.CASCADE,
        verbose_name="Recibo",
        null=True,
        blank=True
    )
    
    image = models.FileField(
        "Arquivo a ser carregado",
        upload_to=upload_to_lancamentos,
        null=True,
        blank=True
    )

    class Meta:
        ordering = ('lcto',)
        verbose_name = "Arquivo do Lançamento"
        verbose_name_plural = "Outros Arquivos do Lançamento"

    def __str__(self):
        return f"Arquivo de {self.lcto.descricao} de {self.lcto.data_vcto.strftime('%d/%m/%Y')}"


class MovimentosCaixa(models.Model):



    TIPOS_MOVIMENTOS_CAIXA = [
        ('SI', 'Saldo Inicial'),
        ('TR', 'Transferência entre contas'),
        ('PG', 'Pagamento'),
        ('PR', 'Recebimento'),
    ]

    tipo = models.CharField(
        "Tipo de movimento",
        max_length=2,
        choices=TIPOS_MOVIMENTOS_CAIXA,
        default='PG',
    )

    lcto_ref = models.ForeignKey(
        PagarReceber,
        models.CASCADE,
        related_name='mov_lcto',
        null=True, 
        blank=True,
        verbose_name="Lançamento de Referência"
    )

    data_lcto = models.DateField(
        "Data de Pagamento",
        db_index=True
    )

    valor = models.DecimalField(
        "Valor",
        max_digits=12,
        decimal_places=2
    )

  
    historico = models.CharField(
        "Histórico - descrição da movimentação",
        max_length=300
    )
    conta_origem = models.ForeignKey(
        Contas,
        models.SET_NULL,
        related_name='mov_conta_origem',
        null=True,
        blank=True,
        verbose_name="Conta de Origem",
        default=None
    )
    conta_destino = models.ForeignKey(
        Contas,
        models.SET_NULL,
        related_name='mov_conta_destino',
        null=True,
        blank=True,
        verbose_name="Conta de Destino",
        default=None
    )


    image = models.FileField(
        "Arquivo a ser carregado",
        upload_to=upload_to_movimentos,
        null=True,
        blank=True
    )

    data_criacao = models.DateTimeField(
        auto_now_add=True, verbose_name="Data de Criação do Movimento")
    data_atualizacao = models.DateTimeField(
        auto_now=True, verbose_name="Data de Atualização do Movimento")
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL,
                                null=True, verbose_name="Usuário responsável pelo Movimento")

    class Meta:
        ordering = ('-data_lcto', "id")
        verbose_name = "Movimentação de Caixa"
        verbose_name_plural = "Movimentações de Caixa"

    def __str__(self):
        return f"{self.historico} em {self.data_lcto.strftime('%d/%m/%Y')} - Valor Pgto : {self.valor} / Valor Lcto : {self.lcto_ref.valor_docto} - Projeto: {self.lcto_ref.centro_custo} - Item Orçamentário: {self.lcto_ref.item_orcamento}" 


class RecibosMaster(models.Model):
    data_recibo = models.DateField('Data do Recibo', db_index=True)

    lancamento = models.ForeignKey(
        PagarReceber,
        related_name='lcto_recibo',
        on_delete=models.CASCADE,
        verbose_name="Lançamento de Referência",
    )

    class Meta:
        ordering = ('-data_recibo', )
        verbose_name = "Recibo"
        verbose_name_plural = "Recibos"

    def __str__(self):
        return f"Recibo de {self.lancamento.descricao} emitido em {self.data_recibo.strftime('%d/%m/%Y')}"
