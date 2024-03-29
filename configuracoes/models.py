from django.db import models
from pessoas.models import Pessoa
from django.contrib import admin


# Create your models here.
class Especie(models.Model):
    descricao = models.CharField(
        "Descrição da Espécie do título",
        max_length=150 
    )
    TIPOS_ESPECIES = [
        ('D', 'Recebimento'),
        ('O', 'Pagamento'),
    ]

    tipo = models.CharField(
        max_length=1,
        choices=TIPOS_ESPECIES,
        default='D',
    )

    """
    # usado para marcar especies de títulos com caráter provisório, ex: adiantamentos
    definitivo = models.BooleanField(
        default=True,
        help_text="Desmarcar se tiver caráter provisório. Exemplo: adiantamento."
    )
    # para exigir número de documento no momento do cadastro
    exige_numero = models.BooleanField("Exige número de documento?",
                                       default=True
                                       )
    exige_arquivo = models.BooleanField("Exige salvar arquivo digital?",
                                        default=False
                                        )
    exige_arquivo = models.BooleanField("Emite recibo?",
                                        default=False
    
                                     )
    """
    observacoes = models.TextField(
        null=True,
        blank=True,
        help_text="Notas ou comentários sobre esta espécie"
    )

    class Meta:
        ordering = ('descricao',)
        verbose_name = "Espécie de Documento"
        verbose_name_plural = "Espécies de Documentos"

    def __str__(self):
        return self.descricao


class Contas(models.Model):
    nome = models.CharField(
        "Nome ou breve descrição da conta",
        max_length=100
    )
    bancaria = models.BooleanField(
        "É uma conta bancária?",
        default=False
    )

    favorecido = models.CharField(
        "Nome do favorecido",
        blank=True,
        null=True,
        max_length=150

    )

    cpf_cnpj = models.CharField(
        "CPF/CNPJ do favorecido:",
        blank=True,
        null=True,
        max_length=150

    )

    numero_banco = models.IntegerField(
        "Número do banco",
        null=True,
        blank=True
    )
    nome_banco = models.CharField(
        "Nome do banco",
        max_length=100,
        null=True,
        blank=True
    )
    numero_agencia = models.SmallIntegerField(
        "Número da agência",
        null=True,
        blank=True
    )
    digito_agencia = models.SmallIntegerField(
        "Dígito da agência",
        null=True,
        blank=True
    )
    numero_conta = models.BigIntegerField(
        "Número da Conta",
        null=True,
        blank=True
    )
    digito_conta = models.SmallIntegerField(
        "Digito da Conta",
        null=True,
        blank=True
    )
    TIPOS_PIX = [
        ('D', 'CPF/CNPJ'),
        ('T', 'Celular'),
        ('E', 'Email'),
        ('B', 'Agência e Conta'),
        ('A', 'Chave Aleatória'),

    ]

    tipo = models.CharField(
        "Tipo da Chave Pix",
        max_length=1,
        choices=TIPOS_PIX,
        default='D',
    )

    chave_pix = models.CharField(
        "Chave Pix",
        max_length=32,
        null=True,
        blank=True
    )

    observacoes = models.TextField(
        "Notas ou comentários sobre esta conta",
        null=True,
        blank=True
    )

    class Meta:
        ordering = ('nome',)
        verbose_name = "Conta da Adeva"
        verbose_name_plural = "Contas da Adeva"

    def __str__(self):
        return self.nome


class CentrosCustos(models.Model):
    descricao = models.CharField(
        "Nome do Projeto",
        max_length=50
    )

    ativa = models.BooleanField(
        "Ativo",
        default=True
    )

    class Meta:
        ordering = ('descricao',)
        verbose_name = "Projeto"
        verbose_name_plural = "Projetos"

    def __str__(self):
        return self.descricao


class ItensOrcamento (models.Model):
    descricao = models.CharField(
        "Item Orçamentário",
        max_length=50
    )

    class Meta:
        ordering = ('descricao',)
        verbose_name = "Item Orçamentário"
        verbose_name_plural = "Itens Orçamentários"

    def __str__(self):
        return self.descricao


class TiposDocumentos (models.Model):
    descricao = models.CharField(
        "Tipo de Documento",
        max_length=50
    )

    class Meta:
        ordering = ('descricao',)
        verbose_name = "Tipo Documento"
        verbose_name_plural = "Tipos Documentos"

    def __str__(self):
        return self.descricao
    
class DescricoesLancamentos (models.Model):
    descricao = models.CharField(
        "Descrição do Lançamento",
        max_length=50
    )

    class Meta:
        ordering = ('descricao',)
        verbose_name = "Descrição Lançamento"
        verbose_name_plural = "Descrições Lançamentos"

    def __str__(self):
        return self.descricao
