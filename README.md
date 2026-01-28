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

**API for analyzing Codeforces profiles that provides useful statistics for improving competitive programming skills.**

**[🌐 Try Live Demo](https://betterforces.deyna.xyz/)**

</div>

## Project Goal

Help competitive programmers and their coaches:
- Identify weak spots in training
- Find knowledge gaps and shortcomings
- Determine strengths
- Track progress and development trends

## Core Features

### Difficulty Distribution
Analyzes the distribution of solved problems by difficulty levels (800, 900, 1000, 1100, etc.).

### Abandoned Problems Analysis
Identifies problems user attempted but never solved, grouped by tags and rating bins.

### Tag Ratings Analysis
Provides average/median rating by problem tags (dp, graphs, greedy, math, etc.).

### Weak Tag Ratings Detection
Automatically identifies topics needing improvement with threshold-based filtering.

## API Endpoints

All endpoints accept a Codeforces handle as a path parameter and return JSON analytics data.

- `GET /difficulty-distribution/{handle}` - Problem count by rating bins (800-3000)
- `GET /tag-ratings/{handle}` - Average/median ratings per problem tag
- `GET /tag-ratings/{handle}/weak` - Weak areas with performance gaps
- `GET /abandoned-problems/by-tags/{handle}` - Failed attempts grouped by tags
- `GET /abandoned-problems/by-ratings/{handle}` - Failed attempts grouped by difficulty

## Technology Stack

### Backend
- **Python 3.13+** - Core language
- **Litestar** - Async web framework
- **Redis** - Caching and rate limiting
- **UV** - Package manager

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first styling
- **Chart.js** - Data visualizations

### Development
- **Docker & Docker Compose** - Container orchestration
- **Just** - Command runner for development tasks

## Getting Started

### Prerequisites
- Docker & Docker Compose (recommended) OR Python 3.13+ with `uv` + Node.js 20+ with `npm` + Redis

### Quick Start with Docker
```bash
git clone https://github.com/yourusername/betterforces.git
cd betterforces
cp .env.example .env
docker-compose up -d

# Access at:
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/schema/swagger
```

### Local Development
```bash
# Install dependencies
just install

# Start Redis
docker run -d -p 6379:6379 redis:7-alpine

# Start backend (from backend/ dir)
cd backend && just dev

# Start frontend (from frontend/ dir)
cd ../frontend && just dev
```

## Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/awesome-feature`)
3. **Make your changes**
4. **Run tests and linting**:
   - Backend: `cd backend && just check && just test`
   - Frontend: `cd frontend && just lint && just typecheck`
5. **Commit your changes** (`git commit -m "Add awesome feature"`)
6. **Push to your branch** (`git push origin feature/awesome-feature`)
7. **Open a pull request**

### Development Commands

**Project Level:**
- `just` - List all commands
- `just up` - Start full stack with Docker
- `just down` - Stop services
- `just logs` - View container logs

**Backend (from backend/ dir):**
- `just dev` - Run development server
- `just test` - Run tests
- `just lint` - Check code style
- `just check` - Lint + typecheck

**Frontend (from frontend/ dir):**
- `just dev` - Run development server
- `just build` - Build for production
- `just lint` - Check code style
- `just typecheck` - TypeScript check

### Architecture

The project follows clean/layered architecture with strict separation:
- **API Layer** - Route handlers, schemas, dependencies
- **Domain Layer** - Pure business logic (no external deps)
- **Infrastructure Layer** - External service integrations
- **Application Services** - Orchestration between layers

---

BetterForces is open-source under the MIT License. Happy coding! 🚀
