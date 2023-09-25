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
    mes = instance.data_vcto.strftime("%m")
    ano = instance.data_vcto.strftime("%Y")
    dia = instance.data_vcto.strftime("%d")
    if (instance.pk is None):
        id = 0
    else:
        id = int(instance.pk)

    name_without_extension, extension = os.path.splitext(filename)
    arquivo = sanitize_filename(dia+'_'+mes+'_'+instance.descricao)
    new_filename = f"doc_{arquivo}_id_{id}{extension}"
    # Construa o caminho completo para upload
    return os.path.join("lancamentos", str(ano), str(mes), new_filename)


def upload_to_movimentos(instance, filename):
    # instance.save()
    # Gere um novo nome de arquivo para evitar conflitos
    mes = instance.data_lcto.strftime("%m")
    ano = instance.data_lcto.strftime("%Y")
    dia = instance.data_lcto.strftime("%d")
    name_without_extension, extension = os.path.splitext(filename)
    arquivo = sanitize_filename(dia+'_'+mes+'_'+instance.historico)
    new_filename = f"compr_{arquivo}_id{instance.pk}{extension}"

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
    valor_docto = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    FORMAS_PGTO = [
        ('BL', 'BOLETO'),
        ('TR', 'TRANSFERÊNCIA'),
        ('ES', 'ESPÉCIE'),
        ('OU', 'OUTRO')
    ]

    forma_pgto = models.CharField("Forma de Pagamento",
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

    class Meta:
        ordering = ('lcto', 'descricao')
        verbose_name = "Detalhe do Lançamento"
        verbose_name_plural = "Detalhes do Lançamento"

    def __str__(self):
        return f"Detalhes de {self.lcto.descricao} de {self.lcto.data_vcto.strftime('%d/%m/%Y')}"


class MovimentosCaixa(models.Model):
    TIPOS_MOVIMENTOS_CAIXA = [
        ('SI', 'Saldo Inicial'),
        ('TR', 'Transferência entre contas'),
        ('PG', 'Pagamento'),
        ('PR', 'Recebimento'),
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
        choices=TIPOS_MOVIMENTOS_CAIXA,
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
    lcto_ref = models.ForeignKey(
        PagarReceber,
        models.SET_NULL,
        related_name='mov_lcto',
        null=True,
        blank=True,
        verbose_name="Lançamento de Referência"
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
        return f"{self.historico} em {self.data_lcto.strftime('%d/%m/%Y')}"


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
        return f"Recibo de {self.lancamento.descricao} emitido em {self.data_rebibo.strftime('%d/%m/%Y')}"
