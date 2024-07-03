FROM python:3.8.19-slim
WORKDIR /app
COPY Pipfile Pipfile.lock /app/

# Install pipenv and PostgreSQL client dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && pip install pipenv \
    && pipenv install --deploy --ignore-pipfile

COPY . /app/
CMD ["pipenv", "run", "python", "src/main.py"]
