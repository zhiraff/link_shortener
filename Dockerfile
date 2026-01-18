FROM python:3.12

ENV PYTHONUNBUFFERED=1
ENV POETRY_VERSION=2.2.1
ENV POETRY_HOME="/opt/poetry"
ENV POETRY_VIRTUALENVS_IN_PROJECTS=true
ENV POETRY_NO_INTERACTION=1
ENV PYSETUP_PATH="/opt/pysetup"
ENV VENV_PATH="/opt/pysetup/.venv"
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

ARG INSTALL_PATH=/srv/rest_api

WORKDIR $INSTALL_PATH

RUN rm -rf /etc/localtime
RUN ln -s /usr/share/zoneinfo/Europe/Moscow /etc/localtime
RUN echo "Europe/Moscow" > /etc/timezone
RUN apt update; apt install graphviz graphviz-dev build-essential -y
# RUN apt -o "Acquire::https::Verify-Peer=false" update ; apt -o "Acquire::https::Verify-Peer=false" install build-essential graphviz graphviz-dev -y
#RUN curl -sSL https://install.python-poetry.org | python -
RUN pip install poetry==2.2.1
ENV PATH="${PATH}:/root/.poetry/bin"
COPY . .
RUN ls -la
RUN echo pyproject.toml
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-root


EXPOSE 8000
ENV PYTHONPATH="${PYTHONPATH}:${INSTALL_PATH}"
CMD ["gunicorn", "-c", "gunicorn.conf.py", "core.wsgi:application"]
