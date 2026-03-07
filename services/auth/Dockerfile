FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY services/auth/pyproject.toml /app/pyproject.toml
COPY services/auth/src /app/src
COPY services/auth/alembic.ini /app/alembic.ini
COPY services/auth/alembic /app/alembic
COPY services/auth/start.sh /app/start.sh
COPY shared /app/shared

RUN uv pip install --system -e /app/shared
RUN uv pip install --system -e /app

RUN chmod +x /app/start.sh

EXPOSE 8001

CMD ["/app/start.sh"]