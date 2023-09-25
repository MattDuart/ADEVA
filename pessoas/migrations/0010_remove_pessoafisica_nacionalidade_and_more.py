# Generated by Django 4.1.6 on 2023-09-25 14:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pessoas', '0009_alter_dadospgto_data_atualizacao_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pessoafisica',
            name='nacionalidade',
        ),
        migrations.RemoveField(
            model_name='pessoafisica',
            name='naturalidade',
        ),
        migrations.RemoveField(
            model_name='pessoafisica',
            name='nome_pai',
        ),
        migrations.RemoveField(
            model_name='pessoafisica',
            name='raca',
        ),
        migrations.RemoveField(
            model_name='pessoajuridica',
            name='tipo_regime',
        ),
        migrations.AlterField(
            model_name='dadospgto',
            name='digito_conta',
            field=models.BigIntegerField(blank=True, null=True, verbose_name='Digito da Conta'),
        ),
        migrations.AlterField(
            model_name='pessoafisica',
            name='cpf',
            field=models.CharField(db_index=True, max_length=20, unique=True),
        ),
        migrations.AlterField(
            model_name='pessoajuridica',
            name='cnpj',
            field=models.CharField(db_index=True, max_length=20, unique=True),
        ),
    ]