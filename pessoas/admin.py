from django.contrib import admin

# Register your models here.
from .models import *


class PFInline(admin.StackedInline):
    model = PessoaFisica
    extra = 1


class PJInline(admin.StackedInline):
    model = PessoaJuridica
    extra = 1


class EnderecoInline(admin.StackedInline):
    model = Endereco
    extra = 1


class TelefoneInline(admin.TabularInline):
    model = Telefone
    extra = 2


class PAInline(admin.TabularInline):
    model = PessoaAtribuicao


class PessoaInline(admin.ModelAdmin):
    model = Pessoa
    inlines = [
        PFInline,
        PJInline,
        EnderecoInline,
        TelefoneInline,
        PAInline
    ]

    class Media:
        js = ("jquery-3.6.3.min.js", "form_pessoa.js",)


@admin.register(DadosPgto)
class DadosPgtoAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        usuario_logado = request.user
        obj.usuario = usuario_logado
        obj.save()
    readonly_fields = ['data_criacao', 'data_atualizacao', 'usuario']


# Register your models here.
admin.site.register(Pessoa, PessoaInline)
# admin.site.register(PessoaFisica)
# admin.site.register(PessoaJuridica)
# admin.site.register(Endereco)
# admin.site.register(Telefone)
admin.site.register(Atribuicao)
# admin.site.register(DadosPgto)
# admin.site.register(PessoaAtribuicao)

admin.site.site_header = 'Sistema Integrado de Gestão Adeva'
admin.site.index_title = 'Administração'
admin.site.site_title = 'Sistema Adeva'
