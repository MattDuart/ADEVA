# Generated by Django 4.1.6 on 2023-09-01 15:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('configuracoes', '0012_remove_contas_pessoa_contas_favorecido'),
    ]

    operations = [
        migrations.AddField(
            model_name='contas',
            name='cpf_cnpj',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='CPF/CNPJ do favorecido:'),
        ),
    ]
