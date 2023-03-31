# Generated by Django 4.1.6 on 2023-02-17 16:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('configuracoes', '0005_centroscustos'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArquivosContabeis',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateField(auto_now=True, db_index=True, verbose_name='Data do upload')),
                ('descricao', models.CharField(max_length=50, verbose_name='Descrição do Arquivo')),
                ('image', models.ImageField(upload_to='documentos', verbose_name='Arquivo a ser carregado')),
            ],
            options={
                'verbose_name': 'Arquivo Suporte Contábil',
                'verbose_name_plural': 'Arquivos de Suporte Contábil',
                'ordering': ('data',),
            },
        ),
        migrations.CreateModel(
            name='PagarReceber',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_lcto', models.DateField(auto_now=True, db_index=True, verbose_name='Data do Lançamento')),
                ('descricao', models.CharField(max_length=100, verbose_name='Descrição do Lançamento')),
                ('data_vcto', models.DateField(db_index=True, verbose_name='Data do Vencimento')),
                ('nro_docto', models.CharField(max_length=25, null=True, verbose_name='Número do Documento')),
                ('valor_docto', models.DecimalField(decimal_places=2, max_digits=12)),
                ('valor_pago', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('status', models.CharField(choices=[('AB', 'Aberto'), ('PP', 'Parcialmente Pago'), ('TP', 'Totalmente Pago')], default='AB', max_length=2, verbose_name='Status do Pagamento')),
                ('observacoes', models.TextField(blank=True, help_text='Notas ou comentários sobre este lançamento', null=True)),
                ('centro_custo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='lcto_cc', to='configuracoes.centroscustos', verbose_name='Projeto')),
                ('especie', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='lcto_especie', to='configuracoes.especie', verbose_name='Espécie do lançamento')),
            ],
            options={
                'verbose_name': 'Conta Pagar/Receber',
                'verbose_name_plural': 'Contas a Pagar/Receber',
                'ordering': ('data_vcto',),
            },
        ),
        migrations.CreateModel(
            name='MovimentosCaixa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_lcto', models.DateField(db_index=True, verbose_name='Data da Movimentação')),
                ('valor', models.DecimalField(decimal_places=2, max_digits=12)),
                ('tipo', models.CharField(choices=[('SI', 'Saldo Inicial'), ('TR', 'Transferência entre contas'), ('PG', 'Pagamento'), ('PR', 'Recebimento')], default='PG', max_length=2, verbose_name='Tipo de movimento')),
                ('historico', models.CharField(max_length=150, verbose_name='Histórico - descrição da movimentação')),
                ('conta_destino', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='mov_conta_destino', to='configuracoes.contas', verbose_name='Conta de Destino')),
                ('conta_origem', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='mov_conta_origem', to='configuracoes.contas', verbose_name='Conta de Origem')),
                ('lcto_ref', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='mov_lcto', to='movimentos.pagarreceber', verbose_name='Lançamento de Referência')),
            ],
            options={
                'verbose_name': 'Movimentação de Caixa',
                'verbose_name_plural': 'Movimentações de Caixa',
                'ordering': ('data_lcto',),
            },
        ),
    ]