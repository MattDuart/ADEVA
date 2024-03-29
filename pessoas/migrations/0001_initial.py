# Generated by Django 4.1.6 on 2023-02-13 14:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Atribuicao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('atribuicao', models.CharField(max_length=50)),
            ],
            options={
                'ordering': ('atribuicao',),
            },
        ),
        migrations.CreateModel(
            name='Pessoa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=250)),
                ('tipo', models.CharField(db_index=True, max_length=1)),
                ('site', models.CharField(blank=True, max_length=150, null=True)),
                ('email', models.CharField(blank=True, max_length=150, null=True)),
            ],
            options={
                'ordering': ('nome', 'tipo'),
            },
        ),
        migrations.CreateModel(
            name='Telefone',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(blank=True, max_length=2, null=True)),
                ('numero', models.CharField(max_length=20)),
                ('pessoa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='telefones', to='pessoas.pessoa')),
            ],
        ),
        migrations.CreateModel(
            name='PessoaJuridica',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cnpj', models.CharField(db_index=True, max_length=14, unique=True)),
                ('nome_fantasia', models.CharField(blank=True, max_length=100, null=True)),
                ('inscricao_estadual', models.CharField(blank=True, max_length=50, null=True)),
                ('inscricao_municipal', models.CharField(blank=True, max_length=50, null=True)),
                ('data_constituicao', models.DateField(blank=True, null=True)),
                ('tipo_regime', models.CharField(blank=True, max_length=1, null=True)),
                ('pessoa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pessoasjuridicas', to='pessoas.pessoa')),
            ],
            options={
                'ordering': ('cnpj',),
            },
        ),
        migrations.CreateModel(
            name='PessoaFisica',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cpf', models.CharField(db_index=True, max_length=11, unique=True)),
                ('rg', models.CharField(blank=True, max_length=20, null=True)),
                ('orgao_rg', models.CharField(blank=True, max_length=20, null=True)),
                ('data_emissao_rg', models.DateField(blank=True, null=True)),
                ('data_nascimento', models.DateField(blank=True, null=True)),
                ('sexo', models.CharField(blank=True, max_length=20, null=True)),
                ('raca', models.CharField(blank=True, max_length=20, null=True)),
                ('nacionalidade', models.CharField(blank=True, max_length=100, null=True)),
                ('naturalidade', models.CharField(blank=True, max_length=100, null=True)),
                ('nome_pai', models.CharField(blank=True, max_length=200, null=True)),
                ('pessoa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pessoasfisicas', to='pessoas.pessoa')),
            ],
            options={
                'ordering': ('cpf',),
            },
        ),
        migrations.CreateModel(
            name='PessoaAtribuicao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('atribuicao', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='atribuicoes', to='pessoas.atribuicao')),
                ('pessoa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pessoas', to='pessoas.pessoa')),
            ],
        ),
        migrations.CreateModel(
            name='Endereco',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('logradouro', models.CharField(max_length=150)),
                ('numero', models.CharField(max_length=10)),
                ('bairro', models.CharField(blank=True, max_length=100, null=True)),
                ('cidade', models.CharField(blank=True, max_length=100, null=True)),
                ('municipio_ibge', models.IntegerField(blank=True, null=True)),
                ('uf', models.CharField(blank=True, max_length=2, null=True)),
                ('cep', models.CharField(blank=True, max_length=8, null=True)),
                ('complemento', models.CharField(blank=True, max_length=100, null=True)),
                ('principal', models.BooleanField(blank=True, default=True, null=True)),
                ('cobranca', models.BooleanField(blank=True, default=True, null=True)),
                ('entrega', models.BooleanField(blank=True, default=True, null=True)),
                ('correspodencia', models.BooleanField(blank=True, default=True, null=True)),
                ('pessoa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='enderecos', to='pessoas.pessoa')),
            ],
        ),
    ]
