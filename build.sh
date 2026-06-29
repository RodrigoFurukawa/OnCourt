#!/usr/bin/env bash
# Build do Render: roda a cada deploy. Falha cedo em qualquer erro.
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate

# Seed inicial (idempotente). Após o primeiro deploy com dados, pode remover esta linha
# para não sobrescrever ajustes feitos pelo admin.
python manage.py seed_data