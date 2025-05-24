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

ALLOWED_HOSTS = ['home-market-place.onrender.com', # Corrected entry
                 'homemarketplace.co.zw', 
                 'www.homemarketplace.co.zw',
                 'localhost',
                 '127.0.0.1']

CSRF_TRUSTED_ORIGINS = [
    'https://home-market-place.onrender.com',
    'https://homemarketplace.co.zw',
    'https://www.homemarketplace.co.zw', # Added missing comma
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
        conn_max_age=600, # set connection max age
        engine='django.db.backends.postgresql' 
    )
}
        
# Redis configuration
# On Render, REDIS_URL will be set in the environment.
# For local Docker Compose, don't set REDIS_URL in .env, if REDIS_URL is not set, default to the 'cache' service.
DEFAULT_DOCKER_REDIS_URL = 'redis://cache:6379'
REDIS_URL_FROM_ENV = os.environ.get('REDIS_URL')

if REDIS_URL_FROM_ENV:
    FINAL_REDIS_URL = REDIS_URL_FROM_ENV
    print(f"[settings/prod.py] Using REDIS_URL from environment: {FINAL_REDIS_URL}")
else:
    FINAL_REDIS_URL = DEFAULT_DOCKER_REDIS_URL
    print(f"[settings/prod.py] REDIS_URL not in environment, defaulting for Docker: {FINAL_REDIS_URL}")

# Ensure CACHES is defined (it should be from base.py, but as a safeguard for direct prod.py use)
if 'CACHES' not in locals() or not isinstance(CACHES, dict) or 'default' not in CACHES:
    CACHES = {'default': {}} 
CACHES['default']['LOCATION'] = FINAL_REDIS_URL
if 'BACKEND' not in CACHES['default'] or not CACHES['default']['BACKEND']:
    CACHES['default']['BACKEND'] = 'django.core.cache.backends.redis.RedisCache'

# Ensure CHANNEL_LAYERS is defined (it should be from base.py, but as a safeguard)
if 'CHANNEL_LAYERS' not in locals() or not isinstance(CHANNEL_LAYERS, dict) or 'default' not in CHANNEL_LAYERS:
    CHANNEL_LAYERS = {'default': {'CONFIG': {'hosts': []}}}
elif 'CONFIG' not in CHANNEL_LAYERS['default']:
    CHANNEL_LAYERS['default']['CONFIG'] = {'hosts': []}
elif 'hosts' not in CHANNEL_LAYERS['default']['CONFIG']:
     CHANNEL_LAYERS['default']['CONFIG']['hosts'] = []

CHANNEL_LAYERS['default']['CONFIG']['hosts'] = [FINAL_REDIS_URL]
if 'BACKEND' not in CHANNEL_LAYERS['default'] or not CHANNEL_LAYERS['default']['BACKEND']:
    CHANNEL_LAYERS['default']['BACKEND'] = 'channels_redis.core.RedisChannelLayer'

# Email settings are primarily inherited from base.py where they use os.getenv()
# Ensure DEFAULT_FROM_EMAIL is set for admin emails too
SERVER_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@homemarketplace.co.zw')
print(f"[settings/prod.py] SERVER_EMAIL set to: {SERVER_EMAIL}")

# Any other prod-specific overrides can go here.