# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '8me9(k9#+g$dv$2nk#3h!8vl#*u-cr^0dlwfp@4(rgi6&=$%ty'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = []


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