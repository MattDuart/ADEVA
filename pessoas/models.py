from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.


class Pessoa(models.Model):
    TIPO_PESSOA = [
        ('J', 'Jurídica'),
        ('F', 'Física')
    ]
    nome = models.CharField(
        max_length=250
    )
    tipo = models.CharField(
        max_length=1,
        db_index=True,
        choices=TIPO_PESSOA,
        default='J'
    )
    site = models.CharField(
        max_length=150,
        null=True,
        blank=True
    )
    email = models.CharField(
        max_length=150,
        null=True,
        blank=True
    )

    class Meta:
        ordering = ('nome', 'tipo',)

    def __str__(self):
        return "%s" % self.nome


# Create your models here.
class PessoaFisica(models.Model):
    pessoa = models.OneToOneField(
        Pessoa,
        related_name='pessoasfisicas',
        on_delete=models.CASCADE
    )
    cpf = models.CharField(
        max_length=20,
        unique=True,
        db_index=True
    )
    rg = models.CharField(
        max_length=20,
        null=True,
        blank=True
    )
    orgao_rg = models.CharField(
        max_length=20,
        null=True,
        blank=True,
    )
    data_emissao_rg = models.DateField(
        null=True,
        blank=True

    )
    data_nascimento = models.DateField(
        null=True,
        blank=True
    )
    sexo = models.CharField(
        max_length=20,
        null=True,
        blank=True

    )
    # raca = models.CharField(
    #    max_length=20,
    #   null=True,
    #   blank=True
    # )
    """
    nacionalidade = models.CharField(
        max_length=100,
        null=True,
        blank = True
    )
    naturalidade = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )
    nome_pai = models.CharField(
        max_length=200,
        null=True,
        blank=True
    )
    """
    class Meta:
        ordering = ('cpf',)
        verbose_name = "Pessoa Física"
        verbose_name_plural = "Pessoas Físicas"

    def __str__(self):
        return self.cpf


class PessoaJuridica(models.Model):
    pessoa = models.OneToOneField(
        Pessoa,
        related_name='pessoasjuridicas',
        on_delete=models.CASCADE
    )
    cnpj = models.CharField(
        max_length=20,
        db_index=True,
        unique=True
    )
    nome_fantasia = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )
    inscricao_estadual = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )
    inscricao_municipal = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )
    data_constituicao = models.DateField(
        null=True,
        blank=True
    )
    # tipo_regime = models.CharField(
    #    max_length=1,
    #    null=True,
    #    blank=True
    # )

    class Meta:
        ordering = ('cnpj',)
        verbose_name = "Pessoa Jurídica"
        verbose_name_plural = "Pessoas Jurídicas"

    def __str__(self):
        return self.cnpj


class Endereco(models.Model):
    UFS = [
        ('AC', 'Acre'),
        ('AL', 'Alagoas'),
        ('AP', 'Amapá'),
        ('AM', 'Amazonas'),
        ('BA', 'Bahia'),
        ('CE', 'Ceará'),
        ('DF', 'Distrito Federal'),
        ('ES', 'Espírito Santo'),
        ('GO', 'Goiás'),
        ('MA', 'Maranhão'),
        ('MT', 'Mato Grosso'),
        ('MS', 'Mato Grosso do Sul'),
        ('MG', 'Minas Gerais'),
        ('PA', 'Pará'),
        ('PB', 'Paraíba'),
        ('PR', 'Paraná'),
        ('PE', 'Pernambuco'),
        ('PI', 'Piauí'),
        ('RJ', 'Rio de Janeiro'),
        ('RN', 'Rio Grande do Norte'),
        ('RS', 'Rio Grande do Sul'),
        ('RO', 'Rondônia'),
        ('RR', 'Roraima'),
        ('SC', 'Santa Catarina'),
        ('SP', 'São Paulo'),
        ('SE', 'Sergipe'),
        ('TO', 'Tocantins')
    ]

    pessoa = models.ForeignKey(
        Pessoa,
        related_name='enderecos',
        on_delete=models.CASCADE
    )
    logradouro = models.CharField(
        max_length=150
    )
    numero = models.CharField(
        max_length=10
    )
    bairro = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )
    cidade = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )
    # municipio_ibge = models.IntegerField(
    #    null=True,
    #    blank=True
    # )
    uf = models.CharField(
        max_length=2,
        choices=UFS,
        default='SP',
        null=True,
        blank=True
    )
    cep = models.CharField(
        max_length=8,
        null=True,
        blank=True
    )
    complemento = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    principal = models.BooleanField(
        null=True,
        blank=True,
        default=True
    )
    cobranca = models.BooleanField(
        null=True,
        blank=True,
        default=True
    )
    entrega = models.BooleanField(
        null=True,
        blank=True,
        default=True
    )
    correspodencia = models.BooleanField(
        null=True,
        blank=True,
        default=True
    )

    class Meta:
        verbose_name = "Endereço"
        verbose_name_plural = "Endereços"

    def __str__(self):
        return self.logradouro


class Telefone(models.Model):
    pessoa = models.ForeignKey(
        Pessoa,
        related_name='telefones',
        on_delete=models.CASCADE
    )
    tipo = models.CharField(
        max_length=2,
        null=True,
        blank=True
    )
    numero = models.CharField(
        max_length=20
    )

    def __str__(self):
        return self.numero


class Atribuicao(models.Model):
    atribuicao = models.CharField(
        max_length=50
    )

    class Meta:
        ordering = ('atribuicao',)
        verbose_name = "Atribuição"
        verbose_name_plural = "Atribuições"

    def __str__(self):
        return self.atribuicao


class PessoaAtribuicao(models.Model):

    pessoa = models.ForeignKey(
        Pessoa,
        related_name='pessoas',
        on_delete=models.CASCADE
    )
    atribuicao = models.ForeignKey(
        Atribuicao,
        related_name='atribuicoes',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Atribuição da Pessoa"
        verbose_name_plural = "Atribuições das Pessoas"


class DadosPgto(models.Model):
    pessoa = models.ForeignKey(
        Pessoa,
        models.CASCADE,
        related_name="pess_conta",
        verbose_name="Pessoa da conta"

    )

    favorecido = models.CharField(
        "Nome do favorecido",
        max_length=100
    )
    documento = models.CharField(
        "CPF ou CNPJ do favorecido",
        max_length=20
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
        default=None,
        null=True,
        blank=True
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
    data_criacao = models.DateTimeField(
        auto_now_add=True, verbose_name="Data de Criação da Conta")
    data_atualizacao = models.DateTimeField(
        auto_now=True, verbose_name="Data de Atualização da Conta")
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                verbose_name="Usuário responsável pela criação da conta")

    class Meta:
        ordering = ('favorecido',)
        verbose_name = "Conta para Pagamento"
        verbose_name_plural = "Cadastro - Contas para Pagamentos"

    def __str__(self):
        return f'{self.pessoa.nome} - Favorecido: {self.favorecido}'
