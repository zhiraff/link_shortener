FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV POETRY_VERSION=2.2.1
ENV POETRY_HOME="/opt/poetry"
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV POETRY_NO_INTERACTION=1

# Системные зависимости
RUN apt-get update && apt-get install -y \
    build-essential \
    graphviz \
    libgraphviz-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Установка poetry
RUN pip install poetry==${POETRY_VERSION}

WORKDIR /app

# Копируем файлы зависимостей отдельно для кэширования
COPY poetry.lock pyproject.toml /app/

# Устанавливаем зависимости - ВАЖНО: без virtualenv внутри контейнера
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-root --only main

# Копируем остальной код
COPY . /app

# Устанавливаем timezone
RUN ln -sf /usr/share/zoneinfo/Europe/Moscow /etc/localtime \
    && echo "Europe/Moscow" > /etc/timezone

EXPOSE 8000

CMD ["gunicorn", "-c", "gunicorn.conf.py", "core.wsgi:application"]
