# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'ia%#0(ar!$m4&^_0tv24dr*rd!$*e7(gye0x&!fx&7yvj@l!)o'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['gia.adeva.org.br', 'www.gia.adeva.org.br']


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'giaadeva_adeva',
        'USER': 'giaadeva_system',
        'PASSWORD': 'jvk9#eTC#j!j',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}


# Configuração do e-mail
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'siga.adeva.org.br'
EMAIL_PORT = 465
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True 
EMAIL_HOST_USER = 'notificacao@siga.adeva.org.br'  # Insira seu endereço de e-mail aqui
EMAIL_HOST_PASSWORD = 'rc4EpFQ^DE@#7XuFp!8'  # Insira sua senha aqui ou utilize variáveis de ambiente


