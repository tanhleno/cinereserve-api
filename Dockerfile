# Stage 1: builder com Poetry
FROM python:3.13-slim AS builder

WORKDIR /app

RUN pip install poetry poetry-plugin-export

COPY pyproject.toml poetry.lock ./

RUN poetry export -f requirements.txt --without-hashes --without dev -o requirements.txt


# Stage 2: imagem final limpa
FROM python:3.13-slim

WORKDIR /app

COPY --from=builder /app/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
