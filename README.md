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

![Build](https://github.com/deyna256/betterforces/actions/workflows/build.yml/badge.svg)
![Website](https://img.shields.io/website?url=https://betterforces.deyna.xyz)

**Identify Your Weak Spots in Competitive Programming**

Track your Codeforces progress, discover knowledge gaps, and improve faster with detailed analytics.

**[🌐 Live Demo](https://betterforces.deyna.xyz/)** | **[📖 Documentation](docs/)** | **[🔌 API Reference](docs/API.md)**

</div>

---

## Why BetterForces?

**The Problem**: You solve hundreds of problems on Codeforces, but don't know which topics need improvement or where to focus your practice.

**The Solution**: BetterForces automatically analyzes your profile to reveal:

- **Activity Timeline** - Your solving activity over any time period with adaptive detail
- **Weak Topics** - Which algorithms and data structures you struggle with
- **Abandoned Problems** - Problems you attempted but never solved (great practice targets!)
- **Difficulty Progression** - How your skills have grown across rating ranges
- **Tag Statistics** - Your average performance on each problem type

Stop guessing where to improve. Start practicing smarter.

---

## Quick Start

```bash
git clone https://github.com/deyna256/betterforces.git
cd betterforces
cp .env.example .env
just build
just up
```

Open **http://localhost:3000** and enter any Codeforces handle to see their analytics.

That's it! 🚀

---

## Features

| Feature | Description |
|---------|-------------|
| **Daily Activity Timeline** | Track your solving activity over time with adaptive granularity (hours to years) |
| **Difficulty Distribution** | Visualize how many problems you've solved at each rating level (800-3500) |
| **Tag Analysis** | See your average and median rating for each topic (DP, graphs, greedy, etc.) |
| **Weak Topics Detection** | Automatically identifies topics where your performance is below average |
| **Abandoned Problems** | Tracks problems you attempted but never solved, grouped by tags or difficulty |
| **Time Period Filtering** | Filter any metric by period (1D, 1W, 1M, 6M, 1Y, All) — no extra API calls |
| **Smart Caching** | Instant responses with stale-while-revalidate pattern (4-hour fresh cache, 24-hour stale) |
| **Rate-Limited Worker** | Respects Codeforces API limits with async task processing |

---

## Tech Stack

- **Backend**: Python 3.13, Litestar (async web framework), Redis (caching + task queue)
- **Worker**: Python 3.13, async task processor with rate limiting
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Chart.js
- **Tooling**: UV package manager, Docker Compose, Just (command runner)

---

## Documentation

- **[Getting Started](docs/DEVELOPMENT.md)** - Development setup and local installation
- **[API Reference](docs/API.md)** - REST API documentation with examples
- **[Architecture](docs/ARCHITECTURE.md)** - System design and technical details
- **[Deployment](docs/DEPLOYMENT.md)** - Production deployment guide
- **[Contributing](CONTRIBUTING.md)** - How to contribute to the project

---

## API Endpoints

All endpoints accept a Codeforces handle as a path parameter:

- `GET /daily-activity/{handle}` - Activity timeline with adaptive granularity
- `GET /difficulty-distribution/{handle}` - Problem count by rating
- `GET /tag-ratings/{handle}` - Average/median ratings per topic
- `GET /tag-ratings/{handle}/weak` - Weak topics with threshold filtering
- `GET /abandoned-problems/by-tags/{handle}` - Failed attempts grouped by tags
- `GET /abandoned-problems/by-ratings/{handle}` - Failed attempts grouped by difficulty

All metric endpoints accept an optional `?period=` query param (`day`, `week`, `month`, `half_year`, `year`, `all_time`).

Interactive documentation: **http://localhost:8000/schema/swagger**

See **[API Reference](docs/API.md)** for detailed examples.

---

## Local Development

**Requirements:** Docker and Docker Compose

```bash
just build   # Build Docker images
just up      # Start all services
just logs    # View logs
just down    # Stop services
```

For local development without Docker, see **[Development Guide](docs/DEVELOPMENT.md)**.

---

## Contributing

We welcome contributions! Please read **[CONTRIBUTING.md](CONTRIBUTING.md)** for guidelines on:

- Branch naming conventions
- Pull request workflow
- CI requirements
- Code review process

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Support

- **Live Demo**: https://betterforces.deyna.xyz
- **Issues**: https://github.com/deyna256/betterforces/issues
- **Discussions**: https://github.com/deyna256/betterforces/discussions

---

<div align="center">
Made with ❤️ for the competitive programming community
</div>
