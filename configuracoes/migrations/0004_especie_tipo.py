# Generated by Django 4.1.6 on 2023-02-17 14:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('configuracoes', '0003_alter_contas_pessoa'),
    ]

    operations = [
        migrations.AddField(
            model_name='especie',
            name='tipo',
            field=models.CharField(choices=[('D', 'Direito'), ('O', 'Obrigação')], default='D', max_length=1),
        ),
    ]
