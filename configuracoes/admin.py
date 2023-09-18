from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
# Register your models here.
# Register your models here.
from .models import Especie, Contas, CentrosCustos, ItensOrcamento


class ContasFormAction(admin.ModelAdmin):
    model = Contas

    class Media:
        js = ("jquery-3.6.3.min.js", "form_pagarreceber.js",)


class CustomUserAdmin(UserAdmin):
    readonly_fields = ('date_joined', 'last_login')


# Registre o modelo de usuário padrão com a classe de administração personalizada
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


# Register your models here.
admin.site.register(Especie)
admin.site.register(Contas, ContasFormAction)
admin.site.register(CentrosCustos)
admin.site.register(ItensOrcamento)
