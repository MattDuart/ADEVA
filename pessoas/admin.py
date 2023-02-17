from django.contrib import admin

# Register your models here.
from .models import *

# Register your models here.
admin.site.register(Pessoa)
admin.site.register(PessoaFisica)
admin.site.register(PessoaJuridica)
admin.site.register(Endereco)
admin.site.register(Telefone)
admin.site.register(Atribuicao)
admin.site.register(PessoaAtribuicao)

admin.site.site_header = 'Sistema Adeva'
admin.site.index_title = 'Administração'                
#admin.site.site_title = 'Sistema Adeva'
