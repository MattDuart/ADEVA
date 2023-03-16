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
        js = ("jquery-3.6.3.min.js","form_pessoa.js",)

# Register your models here.
admin.site.register(Pessoa, PessoaInline)
#admin.site.register(PessoaFisica)
#admin.site.register(PessoaJuridica)
#admin.site.register(Endereco)
#admin.site.register(Telefone)
admin.site.register(Atribuicao)
#admin.site.register(PessoaAtribuicao)

admin.site.site_header = 'Sistema Adeva'
admin.site.index_title = 'Administração'                
admin.site.site_title = 'Sistema Adeva'
