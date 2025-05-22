from .base import *
import os
from django.core.exceptions import ImproperlyConfigured
# import dj_database_url

DEBUG = False

# Security
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True

# Ensure we have a secure SECRET_KEY for production
if not os.getenv('SECRET_KEY'):
    raise ImproperlyConfigured("SECRET_KEY environment variable is required for production")

ALLOWED_HOSTS = ['homemarketplace.onrender.com',
                 'homemarketplace.co.zw', 
                 'www.homemarketplace.co.zw']

ADMINS = [('melo shaya', 'shayanewakomelody02@gmail.com')]

# Configure database using DATABASE_URL environment variable
# DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///db.sqlite3')
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB'),
        'USER': os.environ.get('POSTGRES_USER'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
        'HOST': 'db',
        'PORT': 5432,
    }
    # 'default': dj_database_url.parse(DATABASE_URL)
}
        

REDIS_URL = 'redis://cache:6379'
CACHES['default']['LOCATION'] = REDIS_URL
CHANNEL_LAYERS['default']['CONFIG']['hosts'] = [REDIS_URL]