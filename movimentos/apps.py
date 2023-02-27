from django.apps import AppConfig


class MovimentosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'movimentos'

    def ready(self):
        import movimentos.signals #movimentos is a name of app
