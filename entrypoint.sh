#!/bin/sh

# Выполняем миграции, чтобы создать все таблицы
echo "Applying database migrations..."
python manage.py migrate

# Создаем администратора (если его еще нет)
echo "Creating admin user..."
python manage.py create_admin

# Запускаем основной веб-сервер
echo "Starting Gunicorn..."
gunicorn controlcenter.wsgi --log-file -