# RentSense Control Tower

RentSense Control Tower is a smart rental tracking and fleet intelligence system designed for construction and heavy equipment operations. It centralizes asset utilization tracking, rental lifecycle handoffs, automated anomaly detection, telemetry streaming, and decision recommendations into a high-density, authoritative operational interface.

---

## Project Structure

```
rentsense-control-tower/
│
├── frontend/             # Next.js App Router (TypeScript, Tailwind CSS, Recharts)
│   ├── app/              # Application routes & layouts
│   ├── components/       # Reusable UI & control tower components
│   ├── hooks/            # Custom React hooks (e.g. SSE stream, telemetry)
│   ├── lib/              # Utility functions & API clients
│   ├── types/            # TypeScript type definitions
│   └── public/           # Static assets & QR codes
│
├── backend/              # FastAPI Python Backend
│   ├── app/
│   │   ├── api/          # API route definitions
│   │   ├── core/         # Configuration & security
│   │   ├── db/           # Database session & engine
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Pure business logic & state derivation
│   │   ├── analytics/    # Anomaly rules & forecasting
│   │   ├── seed/         # Database seeding scripts
│   │   └── tests/        # Backend test suite
│   ├── alembic/          # Database migrations
│   ├── requirements.txt  # Python dependencies
│   └── main.py           # Application entrypoint
│
├── simulator/            # Telemetry & event simulator
├── docs/                 # Design & architecture documentation
│   └── design-reference.md # Visual design specification & tokens
│
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore rules
└── README.md             # Project documentation
```

---

## Development Setup

### 1. Environment Configuration

Copy `.env.example` to create your local `.env`:

```bash
cp .env.example .env
```

Set the required configuration values:
- `DATABASE_URL`: PostgreSQL connection string (e.g., Supabase or local Postgres).
- `NEXT_PUBLIC_API_URL`: Backend API URL (default: `http://localhost:8000`).
- `CORS_ORIGINS`: Allowed origins for CORS (default: `http://localhost:3000`).

---

### 2. Backend Setup

From the repository root:

```bash
# Navigate to backend (or execute from root using venv)
cd backend

# Create virtual environment (if not already created)
python -m venv venv

# Activate virtual environment
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the development server
uvicorn main:app --reload --port 8000
```

Verify backend health:
```bash
curl http://localhost:8000/health
# Response: {"status": "ok"}
```

---

### 3. Frontend Setup

From the `frontend` directory:

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

The frontend will be available at `http://localhost:3000`.

To verify production build:
```bash
npm run build
```

---

## Design System Reference

Visual specifications, typography scales, color tokens, and layout guidelines are documented in [`docs/design-reference.md`](docs/design-reference.md).
