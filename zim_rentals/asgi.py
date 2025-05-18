"""
ASGI config for zim_rentals project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
import django
from django.core.asgi import get_asgi_application

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zim_rentals.settings')

# Initialize Django
django.setup()

# Import our routing application (this imports must be after django.setup())
from zim_rentals.routing import application as routing_application

# This application object is used by any ASGI server configured to use this file
application = routing_application
