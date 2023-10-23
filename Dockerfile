FROM python:3.10

WORKDIR /app

COPY requirements.txt requirements.txt
COPY start.sh start.sh
COPY alembic.ini alembic.ini
COPY ./src ./src

RUN pip install --no-cache-dir --upgrade -r requirements.txt

ENTRYPOINT ["/bin/sh", "/app/start.sh"]