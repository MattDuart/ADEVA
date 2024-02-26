# Generated by Django 4.1.6 on 2024-02-26 17:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('configuracoes', '0015_alter_contas_numero_conta_alter_especie_tipo'),
    ]

    operations = [
        migrations.CreateModel(
            name='DescricoesLancamentos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descricao', models.CharField(max_length=50, verbose_name='Descrição do Lançamento')),
            ],
            options={
                'verbose_name': 'Descrição Lançamento',
                'verbose_name_plural': 'Descrições Lançamentos',
                'ordering': ('descricao',),
            },
        ),
        migrations.CreateModel(
            name='TiposDocumentos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descricao', models.CharField(max_length=50, verbose_name='Tipo de Documento')),
            ],
            options={
                'verbose_name': 'Tipo Documento',
                'verbose_name_plural': 'Tipos Documentos',
                'ordering': ('descricao',),
            },
        ),
    ]
