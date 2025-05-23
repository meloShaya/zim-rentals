from .base import *
import os
from django.core.exceptions import ImproperlyConfigured
import dj_database_url

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
                 'www.homemarketplace.co.zw',
                 'localhost',
                 '127.0.0.1']

CSRF_TRUSTED_ORIGINS = [
    'https://*.onrender.com',
    'https://homemarketplace.co.zw',
    'https://www.homemarketplace.co.zw',
    'http://localhost:8080',
    'http://127.0.0.1:8080',
]

ADMINS = [('melo shaya', 'shayanewakomelody02@gmail.com')]

# Configure database using DATABASE_URL environment variable
# DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///db.sqlite3')
database_url = os.environ.get('DATABASE_URL')
if not database_url:
    raise ImproperlyConfigured("DATABASE_URL environment variable is not set.")

DATABASES = {
    'default': dj_database_url.config(
        default=database_url,
        conn_max_age=600, # Optional: set connection max age
        engine='django.db.backends.postgresql' # Explicitly set engine
    )
}
        

REDIS_URL = 'redis://cache:6379'
CACHES['default']['LOCATION'] = REDIS_URL
CHANNEL_LAYERS['default']['CONFIG']['hosts'] = [REDIS_URL]