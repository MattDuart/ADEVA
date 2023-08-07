# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'ia%#0(ar!$m4&^_0tv24dr*rd!$*e7(gye0x&!fx&7yvj@l!)o'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

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
