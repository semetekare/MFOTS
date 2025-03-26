#!/bin/sh

python3 manage.py collectstatic --no-input --clear
python3 manage.py makemigrations
python3 manage.py migrate

python3 manage.py shell <<EOF
from django.contrib.auth import get_user_model

User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser("admin", "admin@example.com", "admin123")
EOF

exec "$@"
