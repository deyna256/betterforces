# BetterForces

<div align="center">
  <img src="logo.svg" alt="BetterForces Logo" width="300"/>
</div>

<div align="center">

![Python 3.13](https://img.shields.io/badge/Python-3.13-blue?style=for-the-badge&logo=python)
![Litestar](https://img.shields.io/badge/Litestar-green?style=for-the-badge&logo=lightning)
![TypeScript](https://img.shields.io/badge/TypeScript-blue?style=for-the-badge&logo=typescript)
![React](https://img.shields.io/badge/React-18-blue?style=for-the-badge&logo=react)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge&logo=opensource)

**Analytics for Codeforces Profiles**

Helps competitive programmers and coaches identify weak spots, track progress, and improve skills through detailed statistics.

**[🌐 Live Demo](https://betterforces.deyna.xyz/)**

</div>

---

## Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [API](#api)
  - [Endpoints](#endpoints)
  - [Response Examples](#response-examples)
- [Architecture](#architecture)
- [Development](#development)
- [Commands](#commands)

---

## Features

| Feature | Description |
|---------|-------------|
| **Difficulty Distribution** | How many problems solved at each rating (800-3000) |
| **Tag Analysis** | Average/median rating by topic (dp, graphs, greedy, etc.) |
| **Weak Topics** | Automatically identifies topics needing improvement |
| **Abandoned Problems** | Problems attempted but never solved |

---

## Quick Start

### Docker (recommended)

```bash
git clone https://github.com/yourusername/betterforces.git
cd betterforces
cp .env.example .env
just build
just up
```

- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/schema/swagger

### Local Development

```bash
# Install dependencies
just install

# Start Redis
docker run -d -p 6379:6379 redis:7-alpine

# Backend
cd backend && just dev

# Frontend (in another terminal)
cd frontend && just dev
```

---

## API

All endpoints accept a Codeforces handle as a path parameter and return JSON analytics.

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/difficulty-distribution/{handle}` | Distribution of solved problems by rating |
| `GET` | `/tag-ratings/{handle}` | Tag statistics (average/median rating) |
| `GET` | `/tag-ratings/{handle}/weak` | Weak topics (with `?threshold=200` parameter) |
| `GET` | `/abandoned-problems/by-tags/{handle}` | Abandoned problems grouped by tags |
| `GET` | `/abandoned-problems/by-ratings/{handle}` | Abandoned problems grouped by rating |

### Response Examples

#### Difficulty Distribution

```bash
GET /difficulty-distribution/tourist
```

```json
{
  "ranges": [
    {"rating": 800, "problem_count": 42},
    {"rating": 900, "problem_count": 38},
    {"rating": 1000, "problem_count": 45}
  ],
  "total_solved": 3157,
  "last_updated": "2026-01-30T12:34:56"
}
```

#### Tag Statistics

```bash
GET /tag-ratings/tourist
```

```json
{
  "tags": [
    {"tag": "dp", "average_rating": 2150.5, "median_rating": 2100, "problem_count": 156},
    {"tag": "graphs", "average_rating": 2080.3, "median_rating": 2000, "problem_count": 142}
  ],
  "overall_average_rating": 1980.5,
  "overall_median_rating": 1900,
  "total_solved": 3157,
  "last_updated": "2026-01-30T12:34:56"
}
```

#### Weak Topics

```bash
GET /tag-ratings/tourist/weak?threshold=200
```

```json
{
  "weak_tags": [
    {"tag": "geometry", "average_rating": 1650.0, "median_rating": 1600, "problem_count": 23}
  ],
  "overall_average_rating": 1980.5,
  "overall_median_rating": 1900,
  "total_solved": 3157,
  "threshold_used": 200,
  "last_updated": "2026-01-30T12:34:56"
}
```

#### Abandoned Problems by Tags

```bash
GET /abandoned-problems/by-tags/tourist
```

```json
{
  "tags": [
    {"tag": "dp", "problem_count": 5, "total_failed_attempts": 18},
    {"tag": "trees", "problem_count": 3, "total_failed_attempts": 12}
  ],
  "total_abandoned_problems": 23,
  "last_updated": "2026-01-30T12:34:56"
}
```

#### Abandoned Problems by Rating

```bash
GET /abandoned-problems/by-ratings/tourist
```

```json
{
  "ratings": [
    {"rating": 2400, "problem_count": 8, "total_failed_attempts": 31},
    {"rating": 2600, "problem_count": 5, "total_failed_attempts": 22}
  ],
  "total_abandoned_problems": 23,
  "last_updated": "2026-01-30T12:34:56"
}
```

---

## Architecture

### Backend (Clean Architecture)

```
backend/
├── api/              # API Layer: routes, schemas, dependencies
├── domain/           # Domain Layer: pure business logic
├── infrastructure/   # Infrastructure: Codeforces API, Redis
└── services/         # Application Services: orchestration
```

**Principles:**
- Async-first (httpx.AsyncClient, redis.asyncio)
- Dependency Injection via Litestar
- Deduplication: only first successful solve counts per problem
- Redis caching (TTL: 4 hours)

### Frontend

```
frontend/src/
├── components/       # React components (Chart.js visualizations)
├── services/         # API client
└── types/            # TypeScript interfaces
```

**Principles:**
- Parallel data fetching (Promise.all)
- TypeScript strict mode
- Tailwind CSS + custom Codeforces color palette

---

## Development

### Requirements

- Python 3.13+ with `uv`
- Node.js 20+ with `npm`
- Redis
- Or just Docker

### Install Dependencies

```bash
just install
```

### Run Tests

```bash
# Backend
cd backend && just test

# Frontend
cd frontend && just typecheck
```

---

## Commands

### Project (root)

| Command | Description |
|---------|-------------|
| `just` | List all commands |
| `just up` | Start all services via Docker |
| `just down` | Stop services |
| `just logs` | View logs |
| `just build` | Build Docker images |

### Backend

| Command | Description |
|---------|-------------|
| `just dev` | Dev server with hot reload |
| `just test` | Run tests |
| `just check` | Linting + typecheck |
| `just lintfix` | Auto-fix linting issues |

### Frontend

| Command | Description |
|---------|-------------|
| `just dev` | Vite dev server |
| `just build` | Production build |
| `just lint` | ESLint check |
| `just typecheck` | TypeScript check |

---

MIT License
