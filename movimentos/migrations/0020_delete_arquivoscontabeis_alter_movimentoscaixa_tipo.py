# Generated by Django 4.1.6 on 2023-08-28 15:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movimentos', '0019_remove_movimentoscaixa_arquivo_suporte_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ArquivosContabeis',
        ),
        migrations.AlterField(
            model_name='movimentoscaixa',
            name='tipo',
            field=models.CharField(choices=[('SI', 'Saldo Inicial'), ('TR', 'Transferência entre contas'), ('PG', 'Pagamento'), ('PR', 'Recebimento')], default='PG', max_length=2, verbose_name='Tipo de movimento'),
        ),
    ]