# ShopStack
## A Production-Ready Microservices E-Commerce Backend

ShopStack is a microservices-based backend platform that demonstrates modern distributed system architecture using FastAPI, PostgreSQL, Redis Streams, Docker, and GitHub Actions CI.
---
The platform implements core e-commerce functionality including:

- Authentication

- Order management

- Event-driven notifications

- API gateway routing

- Distributed rate limiting

- Idempotent request handling

- Observability middleware

- Containerized infrastructure

This project is designed to showcase production-grade backend architecture, DevOps practices, and scalable system design.

---

## Architecture Overview

ShopStack uses a service-oriented architecture with independently deployable services.

                ┌──────────────────┐
                │      Client      │
                │ (Web / Mobile)   │
                └─────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │   API Gateway   │
                 │  FastAPI Proxy  │
                 └───────┬─────────┘
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼

 ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
 │ Auth Service│  │OrdersService│  │Notifications│
 │             │  │             │  │   Worker    │
 │ JWT Auth    │  │ Order CRUD  │  │ Event Proc. │
 │ Rate Limit  │  │ Payments    │  │ RedisStream │
 └──────┬──────┘  └──────┬──────┘  └──────┬──────┘
        │                │                │
        ▼                ▼                ▼

   PostgreSQL       PostgreSQL         Redis
   auth_db          orders_db          Event Bus

---
   
##Microservices
###API Gateway

Entry point for all clients.

Responsibilities:

- Route requests to services

- Provide unified API surface

- Centralized documentation

- Health checks

Endpoints:

/auth/*
/orders/*
/docs
/health

Technology:

- FastAPI

- httpx proxy forwarding

###Auth Service

Handles authentication and authorization.

Features:

- User registration

- Login with JWT

- Password hashing (bcrypt)

- Redis rate limiting

- Token verification

- Structured error responses

Endpoints:

POST /auth/register
POST /auth/login
GET  /auth/verify
GET  /health

Security:

- bcrypt password hashing

- JWT tokens

- Redis login rate limiting

- input validation via Pydantic

Database:

users
Orders Service

Handles all order lifecycle operations.

Features:

Create order

Idempotent order creation

List user orders

Retrieve order

Process payments

Emit domain events

Endpoints:

POST   /orders
GET    /orders
GET    /orders/{id}
POST   /orders/{id}/pay
GET    /health

Database:

orders
order_items
idempotency_keys
Notifications Worker

Background event processor.

Consumes events from Redis Streams.

Events:

order_created
order_paid

Responsibilities:

Email notifications

Event processing

Background job handling

Technology:

Redis Streams

Async worker loop

Consumer groups

Shared Package

The shared module contains reusable components used across services.

Includes:

shopstack_shared/
    observability/
        logging.py
        request_id.py

    contracts/
        events.py

    clients/
        auth_client.py

Purpose:

Avoid duplicate code

Maintain consistent logging

Shared API contracts

Cross-service clients

Technology Stack
Layer	Technology
API Framework	FastAPI
Language	Python 3.12
Database	PostgreSQL
Message Bus	Redis Streams
ORM	SQLAlchemy (Async)
Migrations	Alembic
Containerization	Docker
Dev Environment	uv
Linting	Ruff
Testing	Pytest
CI/CD	GitHub Actions
Project Structure
shopstack/
│
├── services/
│   ├── gateway/
│   │   ├── src/gateway_service/
│   │   └── tests/
│   │
│   ├── auth/
│   │   ├── src/auth_service/
│   │   ├── alembic/
│   │   └── tests/
│   │
│   ├── orders/
│   │   ├── src/orders_service/
│   │   ├── alembic/
│   │   └── tests/
│   │
│   └── notifications/
│       ├── src/notifications_service/
│       └── tests/
│
├── shared/
│   └── src/shopstack_shared/
│
├── infra/
│   └── docker-compose.yml
│
├── .github/
│   └── workflows/ci.yml
│
└── README.md
Running the System
1 Install dependencies

Install uv:

pip install uv
2 Start infrastructure

From project root:

cd infra
docker compose up --build

Services will start:

Gateway        localhost:8000
Auth           localhost:8001
Orders         localhost:8002
Postgres       localhost:5432
Redis          localhost:6379
API Usage Example
Register user
curl -X POST http://localhost:8000/auth/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Password123!"}'
Login
curl -X POST http://localhost:8000/auth/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Password123!"}'

Returns JWT:

{
  "access_token": "...",
  "token_type": "bearer"
}
Create Order
curl -X POST http://localhost:8000/orders/orders \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Idempotency-Key: abc123" \
  -H "Content-Type: application/json" \
  -d '{"currency":"USD","items":[{"sku":"ABC","name":"Widget","qty":2,"unit_price":500}]}'
Pay Order
curl -X POST http://localhost:8000/orders/orders/{order_id}/pay \
  -H "Authorization: Bearer <TOKEN>"
Testing

Run tests inside a service:

cd services/auth
uv run pytest -q

Tests exist for:

auth
orders
gateway
notifications
Linting

Run Ruff:

uv run ruff check .
uv run ruff format .
CI Pipeline

GitHub Actions performs:

Dependency installation

Ruff formatting check

Ruff lint check

Pytest execution

Workflow file:

.github/workflows/ci.yml
Key Engineering Concepts Demonstrated
Microservices Architecture

Services are independently deployable and loosely coupled.

API Gateway Pattern

All traffic enters through a single gateway.

Benefits:

simplified client integration

centralized routing

security enforcement

Event-Driven Architecture

Orders emit events to Redis Streams.

Example:

order_created
order_paid

Notifications service consumes events asynchronously.

Idempotent APIs

Order creation requires:

Idempotency-Key

This prevents duplicate orders during retries.

Rate Limiting

Auth login endpoints are protected with:

Redis-based rate limiter
Observability

All services include:

Request ID middleware
structured logging
Security Considerations

bcrypt password hashing

JWT authentication

rate limiting

request validation

centralized gateway

Future Improvements

Possible extensions:

payment microservice

email delivery system

distributed tracing (OpenTelemetry)

Kubernetes deployment

service discovery

API versioning

caching layer

GraphQL gateway

License

MIT License

Author

Christopher Guzman
Computer Science — Cyber Operations
Augusta University
