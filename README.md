# Company Research Assistant

An AI-powered company research tool built for the Relu Consultancy AI & Automation Developer hiring hackathon. Enter a company name or website URL and get an AI-generated summary, products/services, pain points, competitor analysis, and a downloadable PDF report — all through a ChatGPT-style interface.

**Live demo:** https://company-research-assistant-blond.vercel.app
**Backend API:** https://company-research-assistant-o43o.vercel.app

---

## Features

- Accepts either a company name (e.g. "Tesla") or a website URL (e.g. `https://tesla.com`)
- Uses Serper.dev to find the official website (when only a name is given) and to gather supporting public information
- Crawls key pages of the target site (Home, About, Products, Pricing, Contact) while skipping duplicate and login pages
- Sends cleaned, truncated page content directly to an OpenRouter-hosted LLM (no vector database/RAG — not required for this scope, and unnecessary overhead for a handful of pages)
- Generates a company summary, products/services, AI pain points, and competitor suggestions
- Validates AI-suggested competitors before displaying them
- Produces a downloadable, single-click PDF report
- Optional Discord bot integration — automatically sends the generated PDF and applicant details to a configured channel after each research run
- Every pipeline stage degrades gracefully on failure (see **Architecture** below) — a partial result is always better than a crash

---

## Architecture

```
User input (name or URL)
        │
        ▼
Input resolver ──▶ Serper.dev (find official site, if only a name was given)
        │
        ▼
Website crawler (targeted pages, deduped, capped at 8 pages)
        │
        ▼
Content cleaner (strip HTML noise, truncate per page)
        │
        ▼
OpenRouter AI (summary, products, pain points, competitors)
        │
        ▼
Competitor validation (via Serper)
        │
        ▼
PDF report (base64, returned inline — no persistent storage)
        │
        ▼
Discord send (optional, fire-and-forget background task)
```

**Design principle:** every stage is wrapped in its own try/except. If Serper, the crawler, the AI call, or PDF generation fails, the pipeline logs a warning and continues with whatever data it has — it never crashes the whole request. The `warnings` array in the API response surfaces exactly what degraded, if anything.

---

## Tech stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14 (App Router), TypeScript, Tailwind CSS v4 |
| Backend | FastAPI (Python) |
| Search | Serper.dev |
| AI | OpenRouter (model selectable; defaults to a free-tier model with a multi-model fallback chain) |
| Crawling | httpx + BeautifulSoup |
| PDF generation | fpdf2 |
| Discord | Discord Bot HTTP API |
| Deployment | Vercel (frontend and backend deployed as separate projects) |

---

## Project structure

```
company-research-assistant/
├── frontend/                  Next.js app
│   ├── app/                   Pages (App Router)
│   ├── components/            Sidebar, ReportCard, ProgressIndicator
│   ├── lib/                   API client
│   └── types/                 Shared TypeScript types
│
└── backend/                   FastAPI app
    └── app/
        ├── main.py            Entrypoint, CORS, route registration
        ├── orchestrator.py    Runs the pipeline with per-stage fallback
        ├── routes/            /api/research, /api/discord/send
        ├── services/          One module per pipeline stage
        └── models/            Pydantic schemas
```

---

## Setup instructions

### Prerequisites

- Node.js 18+ and npm
- Python 3.10+
- An [OpenRouter](https://openrouter.ai) API key
- A [Serper.dev](https://serper.dev) API key (free tier available)

### Backend

```bash
cd backend
pip install -r requirements.txt
```

Create a `.env` file in `backend/` (see **Environment variables** below), then run:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`. Interactive docs (Swagger UI) are at `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm install
```

Create a `.env.local` file in `frontend/`:

```
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

Then run:

```bash
npm run dev
```

The app will be available at `http://localhost:3000`.

---

## Environment variables

### Backend (`backend/.env`)

| Variable | Required | Description |
|---|---|---|
| `OPENROUTER_API_KEY` | Yes | API key from [openrouter.ai](https://openrouter.ai/settings/keys) used for AI analysis |
| `SERPER_API_KEY` | Yes | API key from [serper.dev](https://serper.dev) used for website discovery and public search |

### Frontend (`frontend/.env.local`)

| Variable | Required | Description |
|---|---|---|
| `NEXT_PUBLIC_API_BASE_URL` | Yes | Base URL of the deployed (or local) backend API |

Discord bot token, channel ID, and applicant details are entered directly in the app's sidebar at runtime — they are not stored as environment variables, since no persistent storage or accounts are used in this app.

---

## AI model notes

- The default and fallback models are free-tier OpenRouter models (e.g. `meta-llama/llama-3.3-70b-instruct:free`), so the app runs with zero AI cost out of the box.
- The dropdown in the sidebar lets you pick any OpenRouter-supported model.
- If a chosen model is rate-limited, deprecated, or unavailable, the backend automatically walks through a chain of fallback models rather than failing the request. Free-tier models occasionally get renamed or retired by OpenRouter — if a request fails with a 404 for the model, check the current list at `openrouter.ai/models`.

---

## API reference

### `POST /api/research`

```json
{
  "query": "stripe.com",
  "model": "meta-llama/llama-3.3-70b-instruct:free"
}
```

Returns company data, any non-fatal `warnings` from stages that degraded, and a `pdf_url` (base64 data URI, or `null` if PDF generation failed).

### `POST /api/discord/send`

Sends the generated PDF report and applicant/company details to a Discord channel. Runs as a background task — the caller receives an immediate `{"status": "queued"}` response.

### `GET /api/health`

Basic health check, returns `{"status": "ok"}`.

---

## Known limitations

- No database or authentication, by design (not required by the assignment).
- PDF and research results are not persisted between requests — each request is stateless.
- Free-tier AI models have rate limits; under heavy concurrent use, the app may need a paid OpenRouter key for consistent performance.
- Crawling is limited to a small set of common page types and a page-count cap, to keep response times reasonable within Vercel's serverless function duration limits.

---

## Author

Built by Shruti Bhanot for the Relu Consultancy AI & Automation Developer hackathon.