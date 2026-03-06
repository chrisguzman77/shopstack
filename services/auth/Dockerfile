FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY services/auth/pyproject.toml /app/pyproject.toml
COPY services/auth/src /app/src
COPY shared /app/shared

RUN uv pip install --system -e /app/shared
RUN uv pip install --system -e /app

EXPOSE 8001

CMD ["uvicorn", "auth_service.api:app", "--host", "0.0.0.0", "--port", "8001"]