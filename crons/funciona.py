import os
import sys
from django.core.mail import send_mail
from django.conf import settings

# Obtém o diretório do script atual
script_dir = os.path.dirname(os.path.abspath(__file__))

# Adiciona o diretório do projeto ao PYTHONPATH
sys.path.append(os.path.join(script_dir, '..'))

# Configuração do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adeva_project.settings')

# Agora você pode importar as configurações do Django
import django
django.setup()



def send_emails():
    # Lógica para enviar e-mails
    send_mail(
        'Assunto do E-mail de Teste',
        'Este é um e-mail de teste enviado diretamente do shell do Django.',
        'notificacao@siga.adeva.org.br',
        ['matt@solonoi.org'],
    )

if __name__ == "__main__":
    send_emails()
