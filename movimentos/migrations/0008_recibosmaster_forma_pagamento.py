# Generated by Django 4.1.6 on 2023-07-03 12:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movimentos', '0007_recibosmaster_recibodetalhe'),
    ]

    operations = [
        migrations.AddField(
            model_name='recibosmaster',
            name='forma_pagamento',
            field=models.TextField(blank=True, null=True, verbose_name='Forma de Pagamento'),
        ),
    ]
