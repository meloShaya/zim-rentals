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

ALLOWED_HOSTS = ['home-market-place.onrender.com',
                 'homemarketplace.co.zw', 
                 'www.homemarketplace.co.zw',
                 'localhost',
                 '127.0.0.1']

CSRF_TRUSTED_ORIGINS = [
    'https://home-market-place.onrender.com',
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
        
# Redis configuration
redis_url_from_env = os.environ.get('REDIS_URL')
if not redis_url_from_env:
    raise ImproperlyConfigured("REDIS_URL environment variable is not set for production.")

CACHES['default']['LOCATION'] = redis_url_from_env

# Ensure CHANNEL_LAYERS is defined before trying to modify it (it should be imported from base.py)
if 'CHANNEL_LAYERS' not in locals() or not isinstance(CHANNEL_LAYERS, dict):
    # This case should ideally not be hit if base.py properly defines CHANNEL_LAYERS
    # Or if you need a default structure for prod if not in base:
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                'hosts': [],
            },
        },
    }

# Ensure the 'default' key and 'CONFIG' key exist
if 'default' not in CHANNEL_LAYERS:
    CHANNEL_LAYERS['default'] = {'CONFIG': {'hosts': []}}
elif 'CONFIG' not in CHANNEL_LAYERS['default']:
    CHANNEL_LAYERS['default']['CONFIG'] = {'hosts': []}

CHANNEL_LAYERS['default']['CONFIG']['hosts'] = [redis_url_from_env]

# Remove the old REDIS_URL variable if it was just for default fallback
# REDIS_URL = 'redis://cache:6379' # This line can be removed if REDIS_URL is always from env