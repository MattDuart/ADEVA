import sys
sys.path.append('/home/giaadeva/sistema')

from django.core.wsgi import get_wsgi_application

# Restante do código do wsgi.py

import os



os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adeva_project.settings')

application = get_wsgi_application()
