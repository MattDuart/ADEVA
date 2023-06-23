# Generated by Django 4.1.6 on 2023-06-23 14:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('movimentos', '0005_alter_movimentoscaixa_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='movimentoscaixa',
            name='arquivo_suporte',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='mvto_arq', to='movimentos.arquivoscontabeis', verbose_name='Arquivo de Suporte Contábil'),
        ),
        migrations.AlterField(
            model_name='movimentoscaixa',
            name='tipo',
            field=models.CharField(choices=[('SI', 'Saldo Inicial'), ('TR', 'Transferência entre contas'), ('PG', 'Pagamento'), ('PR', 'Recebimento'), ('SP', 'Projetos - Saída para outro projeto'), ('EP', 'Projetos - Entrada de outro projeto')], default='PG', max_length=2, verbose_name='Tipo de movimento'),
        ),
        migrations.AlterField(
            model_name='pagarreceber',
            name='arquivo_suporte',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='lcto_arq', to='movimentos.arquivoscontabeis', verbose_name='Arquivo de Suporte Contábil'),
        ),
        migrations.AlterField(
            model_name='pagarreceber',
            name='nro_docto',
            field=models.CharField(blank=True, max_length=25, null=True, verbose_name='Número do Documento'),
        ),
    ]
