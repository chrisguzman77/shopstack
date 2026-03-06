FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY services/notifications/pyproject.toml /app/pyproject.toml
COPY services/notifications/src /app/src
COPY shared /app/shared

RUN uv pip install --system -e /app/shared
RUN uv pip install --system -e /app

CMD ["python", "-m", "notifications_service.worker"]