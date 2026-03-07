FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY services/notifications/pyproject.toml /app/pyproject.toml
COPY services/notifications/src /app/src
COPY services/notifications/alembic.ini /app/alembic.ini
COPY services/notifications/alembic /app/alembic
COPY services/notifications/start.sh /app/start.sh
COPY shared /app/shared

RUN uv pip install --system -e /app/shared
RUN uv pip install --system -e /app

RUN chmod +x /app/start.sh

CMD ["/app/start.sh"]