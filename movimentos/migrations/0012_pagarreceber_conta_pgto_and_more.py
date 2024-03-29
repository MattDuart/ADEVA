# Generated by Django 4.1.6 on 2023-07-21 13:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pessoas', '0007_alter_dadospgto_pessoa_alter_dadospgto_tipo'),
        ('movimentos', '0011_delete_dadospgto'),
    ]

    operations = [
        migrations.AddField(
            model_name='pagarreceber',
            name='conta_pgto',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='lcto_conta_pgto', to='pessoas.dadospgto', verbose_name='Conta para pagamento(se houver)'),
        ),
        migrations.AlterField(
            model_name='pagarreceber',
            name='codigo_barras',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Código de Barras (se houver)'),
        ),
    ]
