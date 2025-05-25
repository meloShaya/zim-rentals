daphne -p $PORT -b 0.0.0.0 zim_rentals.asgi:application

web: gunicorn zim_rentals.wsgi:application --bind 0.0.0.0:$PORT