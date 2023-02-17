from django.contrib import admin

# Register your models here.
from .models import PagarReceber, MovimentosCaixa, ArquivosContabeis

# Register your models here.
admin.site.register(PagarReceber)
admin.site.register(MovimentosCaixa)
admin.site.register(ArquivosContabeis)