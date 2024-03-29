# Generated by Django 4.1.6 on 2023-07-17 14:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pessoas', '0005_remove_endereco_municipio_ibge_alter_endereco_uf'),
        ('movimentos', '0008_recibosmaster_forma_pagamento'),
    ]

    operations = [
        migrations.AddField(
            model_name='pagarreceber',
            name='codigo_barras',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Código de Barras'),
        ),
        migrations.AlterField(
            model_name='pagarreceber',
            name='pessoa',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='lcto_pess', to='pessoas.pessoa', verbose_name='Pessoa'),
        ),
    ]
