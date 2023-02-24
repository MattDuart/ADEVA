# Generated by Django 4.1.6 on 2023-02-24 12:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('movimentos', '0002_pagarreceber_item_orcamento'),
    ]

    operations = [
        migrations.AddField(
            model_name='pagarreceber',
            name='arquivo_suporte',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='lcto_arq', to='movimentos.arquivoscontabeis', verbose_name='Arquivo de Suporte Contábil'),
        ),
    ]
