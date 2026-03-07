FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY services/orders/pyproject.toml /app/pyproject.toml
COPY services/orders/src /app/src
COPY services/orders/alembic.ini /app/alembic.ini
COPY services/orders/alembic /app/alembic
COPY services/orders/start.sh /app/start.sh
COPY shared /app/shared

RUN uv pip install --system -e /app/shared
RUN uv pip install --system -e /app

RUN chmod +x /app/start.sh

EXPOSE 8002

CMD ["/app/start.sh"]