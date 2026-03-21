# CineReserve

API REST para reserva de assentos em cinemas.

## Requisitos

- Python 3.13
- Poetry
- Docker e Docker Compose

## Instalação
```bash
poetry install
cp .env.example .env
# Edite o .env com sua SECRET_KEY
```

## Gerando uma SECRET_KEY
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Rodando
```bash
docker compose up
docker compose exec app python manage.py migrate
```
