web: gunicorn ecommerce.wsgi:application --workers 3 --timeout 120 --bind 0.0.0.0:$PORT
release: python manage.py migrate