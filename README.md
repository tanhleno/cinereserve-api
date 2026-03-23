# CineReserve

API REST para reserva de assentos em cinemas.

## Sumário

- [Requisitos](#requisitos)
- [Instalação](#instalação)
- [Gerando uma SECRET_KEY](#gerando-uma-secret_key)
- [Endpoints](#endpoints)
- [Rodando](#rodando)
- [Criando um superusuário](#criando-um-superusuário)
- [Dados iniciais](#dados-iniciais)
- [Populando sessões](#populando-sessões)
- [Testes](#testes)

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

As variáveis de conexão (`DB_HOST`, `DB_PORT`, `REDIS_HOST`,
`REDIS_PORT`, `REDIS_DB_INDEX`) são usadas para rodar testes
e comandos de gerenciamento fora do Docker. Altere-as no `.env`
se precisar sobrescrever os valores padrão.

## Gerando uma SECRET_KEY

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Endpoints

### Autenticação

```
POST   /api/v1/auth/register/
POST   /api/v1/auth/login/
POST   /api/v1/auth/refresh/
```

> Obs. 1: `POST /api/v1/auth/register/` espera um corpo JSON com `username`, `email`
> e `password`, ex: `{"username": "joao", "email": "joao@email.com", "password": "senha123"}`.

> Obs. 2: `POST /api/v1/auth/login/` espera `{"email": "joao@email.com", "password": "senha123"}`
> e retorna `access` e `refresh` tokens.

> Obs. 3: `POST /api/v1/auth/refresh/` espera `{"refresh": "<refresh_token>"}` e retorna
> um novo `access` token.

### Catálogo

```
GET    /api/v1/movies/
GET    /api/v1/movies/{movie_id}/sessions/
```

### Reservas

```
GET    /api/v1/sessions/{session_id}/seats/
POST   /api/v1/sessions/{session_id}/reservations/
```

> Obs. 4: `POST  /api/v1/sessions/{session_id}/reservations/` requer autenticação
> e espera um corpo JSON com a chave `seat_ids` contendo uma lista de IDs de assentos,
> ex: `{"seat_ids": [1, 2, 3]}`.

### Pendentes (não implementadas)

```
GET    /api/v1/sessions/{session_id}/reservations/current/
PUT    /api/v1/sessions/{session_id}/reservations/current/
DELETE /api/v1/sessions/{session_id}/reservations/current/
POST   /api/v1/sessions/{session_id}/reservations/current/checkout/

GET    /api/v1/tickets/
GET    /api/v1/tickets/{ticket_id}/
DELETE /api/v1/tickets/{ticket_id}/
```

## Rodando

```bash
docker compose up -d
docker compose exec app python manage.py migrate
```

## Criando um superusuário

```bash
docker compose exec app python manage.py createsuperuser
```

Acesse o admin em `http://localhost:8000/admin/`.

## Dados iniciais

Ao subir o Docker, fixtures de **45 movies** e **3 rooms** são carregadas automaticamente no banco. Para visualizar ou gerenciar esses dados, acesse o Django admin em `http://localhost:8000/admin/`.

## Populando sessões

Sessões expiram naturalmente com o tempo, por isso a decisão foi usar um management command para populá-las sob demanda em vez de fixtures estáticas.

Para criar sessões de teste:

```bash
docker compose exec app python manage.py seed_sessions
```

Por padrão cria 10 sessões nos próximos 7 dias. Opções disponíveis:

```bash
# Criar 20 sessões nos próximos 14 dias
docker compose exec app python manage.py seed_sessions --count 20 --days-ahead 14
```

Para visualizar as sessões criadas, acesse o Django admin em `http://localhost:8000/admin/`.

## Testes

Os testes são independentes dos dados de demonstração — rodam em banco e Redis isolados, sem depender de fixtures ou sessões populadas.

```bash
docker compose up -d
poetry install --with dev
poetry run pytest
```
