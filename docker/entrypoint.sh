#!/bin/sh
set -e

echo "⏳ Attente de PostgreSQL..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.5
done
echo "✅ PostgreSQL est prêt !"

echo "📦 Application des migrations..."
python manage.py migrate users --noinput
python manage.py migrate --noinput

echo "📁 Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

# Crée le superuser si les variables sont définies
if [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
  echo "👤 Création du superuser..."
  python manage.py createsuperuser \
    --noinput \
    --username admin \
    --email $DJANGO_SUPERUSER_EMAIL 2>/dev/null || echo "ℹ️  Superuser déjà existant."
fi

echo "🚀 Démarrage de Gunicorn..."
exec gunicorn config.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 3 \
  --timeout 120 \
  --access-logfile /app/logs/access.log \
  --error-logfile /app/logs/error.log
