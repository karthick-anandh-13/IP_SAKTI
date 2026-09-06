# IP-SAKTI Sahayak — Backend

Backend API for **IP-SAKTI Sahayak**, a multilingual AI assistant for Intellectual
Property and Ayurveda regulatory guidance. This service is the bridge between the
React frontend, the Python RAG retrieval pipeline, the LLM inference service, and
PostgreSQL.

> This repo contains **only the backend**. It does not implement the frontend or
> the RAG retrieval pipeline — the `/ask` endpoint forwards questions to an
> externally running RAG/LLM service and relays its response unmodified.

## Tech Stack

- Python 3.12, FastAPI, Pydantic v2
- PostgreSQL + SQLAlchemy 2.0 (ORM)
- JWT auth (python-jose) + BCrypt password hashing (passlib)
- httpx for the AI gateway forward call
- Docker / docker-compose
- Node.js (Axios) for seeding and API smoke testing

## Folder Structure

```
backend/
├── app/
│   ├── auth/            # JWT auth: router, service, dependencies, jwt_handler
│   ├── chat/             # Chat sessions/messages + /ask AI gateway router
│   ├── documents/        # Legal/regulatory document metadata CRUD
│   ├── feedback/         # User feedback on chat sessions
│   ├── models/           # SQLAlchemy ORM models
│   ├── schemas/          # Pydantic request/response schemas
│   ├── services/         # ai_gateway.py — forwards /ask to the RAG service
│   ├── database.py       # Engine, session factory, declarative base
│   ├── config.py         # Environment-driven settings
│   └── main.py           # FastAPI app, routers, error handlers, CORS
├── scripts/
│   ├── seed.js            # Seeds sample users + documents via the API
│   └── test-api.js        # Axios smoke tests for every endpoint
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

## Running Locally (Docker)

```bash
cp .env.example .env        # edit JWT_SECRET_KEY, RAG_SERVICE_URL, etc.
docker compose up --build
```

This starts Postgres on `5432` and the backend on `8080`. On startup, the
backend auto-creates tables via SQLAlchemy metadata (swap for Alembic
migrations in a real production rollout).

Swagger UI: http://localhost:8080/docs
ReDoc: http://localhost:8080/redoc
OpenAPI JSON: http://localhost:8080/openapi.json

## Running Locally (without Docker)

```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Make sure Postgres is running and DATABASE_URL in .env points to it
uvicorn app.main:app --reload --port 8080
```

## Node.js Utility Scripts

```bash
cd scripts
npm install

BASE_URL=http://localhost:8080 npm run seed        # sample users + documents
BASE_URL=http://localhost:8080 npm run test-api    # smoke test every endpoint
```

## Environment Variables

| Variable                       | Description                                     | Default                                              |
|---------------------------------|--------------------------------------------------|-------------------------------------------------------|
| `DATABASE_URL`                  | Postgres connection string (SQLAlchemy format)   | `postgresql+psycopg2://ipsakti:ipsakti_pass@localhost:5432/ipsakti_db` |
| `JWT_SECRET_KEY`                | Secret used to sign JWTs — **change in prod**    | insecure placeholder                                  |
| `JWT_ALGORITHM`                 | JWT signing algorithm                            | `HS256`                                                |
| `ACCESS_TOKEN_EXPIRE_MINUTES`   | Token lifetime                                   | `1440` (24h)                                           |
| `RAG_SERVICE_URL`               | URL of the external RAG/LLM `/query` endpoint    | `http://localhost:8000/query`                          |
| `RAG_REQUEST_TIMEOUT_SECONDS`   | Timeout when forwarding to the RAG service       | `60`                                                   |
| `CORS_ORIGINS`                  | Allowed frontend origins (JSON array)            | `["http://localhost:3000","http://localhost:5173"]`    |

## API Reference

### Authentication

| Method | Path            | Auth | Description                     |
|--------|-----------------|------|----------------------------------|
| POST   | `/auth/register`| No   | Create an account, returns JWT   |
| POST   | `/auth/login`   | No   | Log in, returns JWT              |
| GET    | `/auth/me`      | Yes  | Get the current user's profile   |

### Chat

| Method | Path                       | Auth | Description                      |
|--------|----------------------------|------|------------------------------------|
| POST   | `/chat/session`            | Yes  | Create a new chat session          |
| GET    | `/chat/sessions`           | Yes  | List the caller's chat sessions    |
| GET    | `/chat/{id}`               | Yes  | Get a session + its messages       |
| POST   | `/chat/{id}/message`       | Yes  | Append a message to a session      |
| DELETE | `/chat/{id}`               | Yes  | Delete a session (cascades msgs)   |

### AI Gateway

| Method | Path   | Auth | Description                                             |
|--------|--------|------|-----------------------------------------------------------|
| POST   | `/ask` | Yes  | Forwards `{question, language, session_id}` to the RAG/LLM service (`RAG_SERVICE_URL`) and returns its JSON response unmodified. |

### Documents

| Method | Path               | Auth | Description                    |
|--------|--------------------|------|----------------------------------|
| GET    | `/documents`       | No   | List documents (filterable)      |
| POST   | `/documents`       | Yes  | Add document metadata            |
| GET    | `/documents/{id}`  | No   | Get one document                 |
| DELETE | `/documents/{id}`  | Yes  | Delete a document                |

### Feedback

| Method | Path        | Auth | Description                         |
|--------|-------------|------|----------------------------------------|
| POST   | `/feedback` | No   | Submit rating/comment for a session    |
| GET    | `/feedback` | No   | List feedback (optionally by session)  |

## Example curl Requests

```bash
# Register
curl -X POST http://localhost:8080/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Karthick","email":"karthick@example.com","password":"SecurePass123"}'

# Login
curl -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"karthick@example.com","password":"SecurePass123"}'

# Get current user (replace TOKEN)
curl http://localhost:8080/auth/me -H "Authorization: Bearer TOKEN"

# Create a chat session
curl -X POST http://localhost:8080/chat/session \
  -H "Authorization: Bearer TOKEN" -H "Content-Type: application/json" \
  -d '{"title":"Prior Art Query","language":"en"}'

# Ask a question (forwarded to the RAG/LLM service)
curl -X POST http://localhost:8080/ask \
  -H "Authorization: Bearer TOKEN" -H "Content-Type: application/json" \
  -d '{"question":"What is prior art?","language":"en","session_id":"SESSION_ID"}'

# List documents
curl http://localhost:8080/documents

# Submit feedback
curl -X POST http://localhost:8080/feedback \
  -H "Content-Type: application/json" \
  -d '{"session_id":"SESSION_ID","rating":5,"comment":"Helpful and well-cited."}'
```

## Postman

1. Import the OpenAPI spec directly: in Postman, **Import → Link** →
   `http://localhost:8080/openapi.json` (with the server running), which
   generates a full collection with every route, schema, and example body.
2. Create a Postman environment with a `base_url` variable
   (`http://localhost:8080`) and a `token` variable populated from the
   `/auth/login` response, then set collection-level auth to
   **Bearer Token** → `{{token}}`.

## Notes on Production Hardening

- Swap `Base.metadata.create_all` in `main.py` for Alembic migrations.
- Set a strong, random `JWT_SECRET_KEY` and store secrets in a vault, not `.env`.
- Put the backend behind HTTPS/TLS termination (reverse proxy / load balancer).
- Add rate limiting in front of `/auth/login` and `/ask` to curb abuse.
- Add structured logging/observability (request IDs, latency, RAG call timing).
