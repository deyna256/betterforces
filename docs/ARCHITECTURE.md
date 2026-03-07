# Architecture

BetterForces uses an async processing architecture with stale-while-revalidate caching to handle Codeforces API rate limiting.

## System Overview

```
┌──────────────┐
│   Frontend   │  ← Polling with exponential backoff, stale data indicators
│  (React/TS)  │
└──────┬───────┘
       │ HTTP/REST
       ▼
┌──────────────────────────────────────────────────────────┐
│              Backend API (Litestar)                       │
│                                                           │
│  Stale-While-Revalidate Pattern:                         │
│  • Fresh data (< 4h):  200 OK + data                     │
│  • Stale data (4-24h): 200 OK + stale + background job   │
│  • No data:            202 Accepted + task_id (polling)  │
└──────┬───────────────────────────────────────────────────┘
       │
       │ Redis (Queue + Cache)
       ▼
┌──────────────────────────────────────────────────────────┐
│  Worker Process (Rate-Limited Task Processor)            │
│  • Token bucket: 5 requests/sec to Codeforces API        │
│  • BLPOP queue processing with deduplication             │
│  • Graceful shutdown handling                            │
└──────┬───────────────────────────────────────────────────┘
       │
       │ HTTPS (max 5 req/sec)
       ▼
┌──────────────────┐
│  Codeforces API  │
└──────────────────┘
```

## Backend Architecture (Clean Architecture)

The backend follows a layered architecture with strict separation of concerns:

```
┌─────────────────────────────────┐
│  API Layer (backend/api/)       │  ← Route handlers, schemas, dependency injection
│  - app.py: Litestar app factory │
│  - routes/: Controller handlers │
│  - schemas/: Pydantic models    │
│  - deps.py: DI providers        │
└─────────────┬───────────────────┘
              │
┌─────────────▼───────────────────┐
│  Domain Layer (backend/domain/) │  ← Pure business logic (no external deps)
│  - models/: Domain entities     │
│  - services/: Business logic    │
└─────────────┬───────────────────┘
              │
┌─────────────▼───────────────────┐
│  Infrastructure Layer           │  ← External service integrations
│  (backend/infrastructure/)      │
│  - codeforces_client.py         │
│  - redis_client.py              │
│  - task_queue.py                │
└─────────────┬───────────────────┘
              │
┌─────────────▼───────────────────┐
│  Application Services           │  ← Orchestration between layers
│  (backend/services/)            │
│  - codeforces_data_service.py  │
└─────────────┬───────────────────┘
              │
┌─────────────▼───────────────────┐
│  Worker Process                 │  ← Async task processor
│  (backend/worker/)              │
│  - main.py: Worker + RateLimiter│
└─────────────────────────────────┘
```

### Backend Principles

1. **Async-First**: All I/O operations use async/await (httpx.AsyncClient, redis.asyncio)
2. **Dependency Injection**: Litestar's `@Provide` decorator injects services into route handlers
3. **BaseService/BaseController**: Shared utilities in base classes (deduplication, filtering, cache headers)
4. **Domain Model Separation**: Domain models are independent dataclasses; API schemas are Pydantic models
5. **Error Handling**: Custom exceptions (`CodeforcesAPIError`, `UserNotFoundError`) with specific HTTP status codes
6. **Configuration**: Centralized in `backend/config.py` using Pydantic BaseSettings (loads from .env)

### Data Flow Example

```
HTTP Request → Route Handler → Check Redis Cache
                                      │
                    ┌─────────────────┴─────────────────┐
                    │                                   │
              Fresh (< 4h)                        Stale/No Data
                    │                                   │
                    ▼                                   ▼
            Return 200 OK                    Stale: Return 200 + enqueue job
                                             No data: Return 202 + task_id
                                                     │
                                                     ▼
                                            Worker processes task
                                                     │
                                                     ▼
                                            Fetch from Codeforces API
                                                     │
                                                     ▼
                                            Cache for 24h + update task status
```

### Key Backend Features

**Submission Deduplication:**
- `SubmissionCollection.deduplicate_problems()` keeps only the first solve per problem
- Problems identified by `(contest_id, index)` tuple
- Critical for accurate statistics since users may solve problems multiple times

**Redis Caching:**
- Two Redis stores: `"default"` (data caching) and `"rate_limit"` (rate limiting)
- Fresh data TTL: 4 hours (configurable via `settings.cache_fresh_ttl`)
- Stale data TTL: 24 hours (configurable via `settings.cache_stale_ttl`)

**Redis Keys Structure:**
```
submissions:{handle}          # TTL: 24h - Cached submission data
fetch_queue                   # No TTL - Task queue (List)
task:{task_id}:status         # TTL: 5min - Task status (processing/completed/failed)
task:{task_id}:result         # TTL: 5min - Task result data
task:{task_id}:error          # TTL: 5min - Task error message
task:{task_id}:handle         # TTL: 5min - Reverse lookup (task_id → handle)
pending_task:{handle}         # TTL: 60s - Deduplication lock (handle → task_id)
```

**Async Processing & Task Queue:**
- Worker process runs in separate Docker container
- Token bucket rate limiter enforces 5 requests/second to Codeforces API
- BLPOP-based queue processing with graceful shutdown (SIGINT/SIGTERM)
- Three levels of deduplication:
  1. Quick check: `pending_task:{handle}` key
  2. Atomic SETNX: Set only if not exists
  3. Related task update: Worker notifies concurrent requests

**Stale-While-Revalidate Pattern:**
- Fresh (< 4h): Return immediately with remaining TTL in Cache-Control
- Stale (4-24h): Return stale data + enqueue background refresh (non-blocking)
- No data: Return 202 Accepted + task_id for polling
- Frontend polls `/tasks/{task_id}` with exponential backoff (2s → 10s max)

## Frontend Architecture

### Component Structure

```
frontend/src/
├── App.tsx              # Main container with state management + parallel API fetching
├── components/
│   ├── charts/          # Chart.js visualizations (bar + radar charts)
│   └── layout/          # Reusable UI components (Header, StatCard)
├── services/
│   └── api.ts           # Axios client with typed endpoints
└── types/
    └── api.ts           # TypeScript interfaces for all API responses
```

### Frontend Principles

1. **Simple State Management**: React hooks (useState, useEffect) - no Redux needed
2. **Parallel Data Fetching**: `Promise.all()` fetches multiple endpoints simultaneously
3. **Type Safety**: All API responses and components fully typed with TypeScript strict mode
4. **Chart.js Integration**: Both Bar and Radar chart types with custom configurations
5. **Tailwind CSS**: Utility-first styling with custom Codeforces color palette
6. **Vite Dev Proxy**: `/api` requests proxied to backend at localhost:8000
7. **Async Polling**: Exponential backoff (2s → 10s max) for 202 Accepted responses
8. **Stale Data Indicators**: Yellow banner with data age and "Refresh Now" button

### Chart Data Preparation

- Always filter difficulty ranges to 800-3000 (ignore unrated/outliers)
- Top 15 tags sorted by count for better visualization
- Radar charts use subset of data for readability

### Polling Implementation

- `fetchWithPolling()` wrapper handles 202 Accepted responses
- `pollTask()` with exponential backoff: 2s → 3s → 4.5s → 6.75s → max 10s
- Max 30 polling attempts (≈2-3 minutes timeout)
- Automatic retry on transient failures
- Returns both data and metadata (`{ data, metadata: { isStale, dataAge } }`)

## File Structure

```
betterforces/
├── backend/                  # Python backend
│   ├── api/                 # API layer (routes, schemas)
│   │   └── routes/
│   │       ├── base.py             # BaseMetricController
│   │       ├── tasks.py            # Task status polling
│   │       └── ...
│   ├── domain/              # Domain layer (business logic)
│   ├── infrastructure/      # Infrastructure (external services)
│   │   ├── codeforces_client.py
│   │   ├── redis_client.py
│   │   └── task_queue.py
│   ├── services/            # Application services
│   ├── worker/              # Async task processor
│   │   └── main.py
│   └── tests/               # Backend tests
├── frontend/                # React frontend
│   └── src/
│       ├── components/
│       ├── services/
│       └── types/
└── docs/                    # Documentation
    ├── API.md
    ├── ARCHITECTURE.md
    ├── DEVELOPMENT.md
    └── DEPLOYMENT.md
```

## Docker Services

The application runs as 4 Docker containers:

**Backend:**
- Port: 8000
- Health check: GET /schema/openapi.json
- Dependencies: redis
- Hot reload enabled in DEV_MODE

**Frontend:**
- Port: 3000
- Nginx serving static React build
- Proxy /api → backend:8000
- Dependencies: backend

**Worker:**
- No exposed ports
- Processes tasks from Redis queue
- Rate-limited: 5 req/sec to Codeforces API
- Dependencies: redis
- Auto-restart on failure

**Redis:**
- Port: 6379 (internal only)
- Persistent volume: redis_data
- Used for: cache, task queue, task status
