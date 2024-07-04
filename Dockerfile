# Ce fichier Dockerfile construit une image en utilisant https://docs.docker.com/build/building/multi-stage/ (Docker Multi-Stage build).
# Nous utilisons d'abord l'image Alpine publique dans la phase build
FROM python:3.8.19-alpine AS builder

WORKDIR /app

COPY Pipfile Pipfile.lock /app/

# Puisque nous sommes sur Alpine, nous utilisons apk (Alpine Package Manager) pour installer les dependances du projet
# Optimization 1 : --no-cache empeche Alpine de mettre en cache certaines informations tel que l'index du package.
# Optimization 2 : --no-cache-dir empeche pip de mettre en cache les fichiers du package
# PIPENV_VENV_IN_PROJECT=1 {...} cree l'environnement virtuel pour pipenv dans /app (utile pour recopier l'environnement plus tard)

RUN apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev libffi-dev && \
    apk add --no-cache libpq && \
    pip install --no-cache-dir pipenv && \
    PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy --ignore-pipfile


# Nous passons a la deuxieme phase. Une fois le build fini, nous commencons fraiche via une nouvelle image.

FROM python:3.8.19-alpine

WORKDIR /app

RUN apk add --no-cache libpq

# Copier les fichiers que nous avons generes dans la phase build

COPY --from=builder /app /app

RUN pip install --no-cache-dir pipenv

COPY . /app/

ENV PATH="/app/.venv/bin:$PATH"

ENV PIPENV_PYTHON=/usr/local/bin/python

CMD ["pipenv", "run", "python", "src/main.py"]
