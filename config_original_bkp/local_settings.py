from pathlib import Path
import os
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-c9dr50$(zsy181n0q^7w0d7^u1k)^w4i$51*i_%^rp)ccywoqc'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'adeva',
        'USER': 'root',
        'PASSWORD': 'adeva',
        'HOST': 'localhost',
        'PORT': '',
    }
}


