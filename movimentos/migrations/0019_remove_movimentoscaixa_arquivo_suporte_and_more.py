# Generated by Django 4.1.6 on 2023-08-14 15:45

from django.db import migrations, models
import movimentos.models


class Migration(migrations.Migration):

    dependencies = [
        ('movimentos', '0018_pagarreceber_image_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='movimentoscaixa',
            name='arquivo_suporte',
        ),
        migrations.RemoveField(
            model_name='pagarreceber',
            name='arquivo_suporte',
        ),
        migrations.AddField(
            model_name='movimentoscaixa',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=movimentos.models.upload_to_movimentos, verbose_name='Arquivo a ser carregado'),
        ),
        migrations.AlterField(
            model_name='pagarreceber',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=movimentos.models.upload_to_lancamentos, verbose_name='Arquivo a ser carregado'),
        ),
    ]
