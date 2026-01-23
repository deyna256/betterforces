# BetterForces Frontend

Modern web interface for BetterForces Codeforces analytics platform.

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type-safe JavaScript
- **Vite** - Fast build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **Chart.js** - Data visualization library
- **Axios** - HTTP client for API requests

## Features

- Real-time Codeforces profile analysis
- Interactive charts for metrics visualization
- Responsive design for all screen sizes
- Fast loading with optimized builds
- Type-safe API integration

## Development

### Install Dependencies

```bash
npm install
```

### Start Dev Server

```bash
npm run dev
```

Development server runs at `http://localhost:3000`

### Build for Production

```bash
npm run build
```

Output will be in the `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

## Environment Variables

Create a `.env` file (copy from `.env.example`):

```env
VITE_API_URL=http://localhost:8000/api
```

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── charts/           # Chart components (Chart.js)
│   │   │   ├── AbandonedProblemsChart.tsx
│   │   │   ├── DifficultyDistributionChart.tsx
│   │   │   └── TagsChart.tsx
│   │   └── layout/           # Layout components
│   │       ├── Header.tsx
│   │       └── StatCard.tsx
│   ├── services/
│   │   └── api.ts            # API client (Axios)
│   ├── types/
│   │   └── api.ts            # TypeScript type definitions
│   ├── App.tsx               # Main application component
│   ├── main.tsx              # Application entry point
│   └── index.css             # Global styles (Tailwind)
├── public/                   # Static assets
├── index.html                # HTML template
├── vite.config.ts            # Vite configuration
├── tailwind.config.js        # Tailwind CSS configuration
├── tsconfig.json             # TypeScript configuration
└── package.json              # Dependencies and scripts
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Docker

Build and run with Docker:

```bash
# Build image
docker build -t betterforces-frontend .

# Run container
docker run -p 3000:80 betterforces-frontend
```

## Contributing

See the main project README for contribution guidelines.
