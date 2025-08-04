#!/bin/sh

echo "🟡 Waiting for database..."
while ! nc -z db 3306; do
  sleep 1
done

echo "✅ Database is up!"

python manage.py migrate
python manage.py collectstatic --noinput
python manage.py runserver 0.0.0.0:8000
