# Generated by Django 4.1.6 on 2023-03-17 15:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('configuracoes', '0007_alter_especie_definitivo'),
    ]

    operations = [
        migrations.AddField(
            model_name='contas',
            name='tipo',
            field=models.CharField(choices=[('D', 'CPF/CNPJ'), ('T', 'Celular'), ('E', 'Email'), ('B', 'Agência e Conta'), ('A', 'Chave Aleatória')], default='D', max_length=1, verbose_name='Tipo da Chave Pix'),
        ),
    ]
