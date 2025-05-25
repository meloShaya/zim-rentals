from .base import *
import os

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Development specific email backend (prints to console)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


# For django-allauth, ensure generated URLs use http in local development
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'http'

# Database (example for local SQLite, override if you use Docker locally for Postgres)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

    

# Static files (served by Django in DEBUG mode)
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage' # Not whitenoise for local usually

# Ensure debug_toolbar is active if DEBUG is True (base.py should handle this)
# However, explicitly ensuring INTERNAL_IPS for debug_toolbar if needed:
INTERNAL_IPS = [
    '127.0.0.1',
]

print("[settings/local.py] Loaded local settings.")
print(f"[settings/local.py] EMAIL_BACKEND set to: {EMAIL_BACKEND}")
print(f"[settings/local.py] ACCOUNT_DEFAULT_HTTP_PROTOCOL set to: {ACCOUNT_DEFAULT_HTTP_PROTOCOL}")