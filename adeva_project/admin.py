from django.contrib import admin
from django.apps import apps


class MyAdminSite(admin.AdminSite):
    def get_app_list(self, request, app_label=None):
        """
        Return a sorted list of all the installed apps that have been
        registered in this site.
        """
        app_dict = self._build_app_dict(request, app_label)

        # Sort the apps alphabetically.
        # app_list = sorted(app_dict.values(), key=lambda x: x["name"].lower())

        def my_key(app):
            # lista de ordenação pré-definida
            ordering_list = ['Movimentos', 'Pessoas', 'Configurações']
            app_name = app['name']

            if app_name in ordering_list:
                # retorna um tupla com dois valores:
                # o índice do modelo na lista de ordenação pré-definida (menor vem primeiro)
                # o nome do modelo (para o caso de empates na primeira comparação)
                return ordering_list.index(app_name), app_name
            else:
                # retorna apenas o nome do modelo
                return len(ordering_list), app_name

        app_list = sorted(app_dict.values(), key=my_key)

        def my_model_key(model):
            # lista de ordenação pré-definida
            ordering_list = ['Contas a Pagar/Receber',
                             'Movimentações de Caixa']
            model_name = model['name']
            if model_name in ordering_list:
                # retorna um tupla com dois valores:
                # o índice do modelo na lista de ordenação pré-definida (menor vem primeiro)
                # o nome do modelo (para o caso de empates na primeira comparação)
                return ordering_list.index(model_name), model_name
            else:
                # retorna apenas o nome do modelo
                return len(ordering_list), model_name

        # Sort the models alphabetically within each app.
        for app in app_list:
            if app['name'] == 'Movimentos':
                app["models"].sort(key=my_model_key)
            else:
                app["models"].sort(key=lambda x: x["name"])

        return app_list
