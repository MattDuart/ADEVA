# Generated by Django 4.1.6 on 2023-06-16 14:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('configuracoes', '0008_contas_tipo'),
    ]

    operations = [
        migrations.AddField(
            model_name='centroscustos',
            name='ativa',
            field=models.BooleanField(default=True, verbose_name='Ativo'),
        ),
    ]
