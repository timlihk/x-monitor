# X Monitor

A lightweight personal web app to track keywords, tickers, and hashtags on X.com (Twitter) using the X Premium API. The app runs on a daily schedule, summarizes tweets with LLM, and presents results in a simple web dashboard.

## Features

- ✅ Monitor keywords/hashtags/tickers (e.g., `$ORCL`, `#AI`)
- ✅ Toggle: restrict results only to accounts you follow
- ✅ Daily scheduled fetch from X API
- ✅ Summarize results with OpenAI/Claude
- ✅ Web dashboard to view latest summaries + top tweets
- ✅ REST API for configuration and results
- ✅ SQLite for local dev, ready for Postgres in production

## Tech Stack

- **Backend:** Python (FastAPI)
- **Frontend:** React + Vite + Tailwind CSS
- **Database:** SQLite (dev), Postgres (prod)
- **Scheduler:** APScheduler
- **Integrations:** X API v2, OpenAI/Claude API

## Setup

### 1. Clone and Setup Backend

```bash
cd backend
pip install -r requirements.txt

# Copy environment template
cp ../.env.example .env

# Edit .env with your API keys
nano .env
```

### 2. Configure X API

Get your X API credentials from [developer.twitter.com](https://developer.twitter.com) and add them to `.env`:

```env
X_API_KEY=your_api_key
X_API_SECRET=your_api_secret  
X_BEARER_TOKEN=your_bearer_token
X_ACCESS_TOKEN=your_access_token
X_ACCESS_TOKEN_SECRET=your_access_token_secret
```

### 3. Configure LLM API

Add either OpenAI or Anthropic API key:

```env
# Option 1: OpenAI
OPENAI_API_KEY=your_openai_key

# Option 2: Anthropic Claude
ANTHROPIC_API_KEY=your_anthropic_key
```

### 4. Initialize Database

```bash
cd backend
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### 5. Setup Frontend

```bash
cd frontend
npm install
```

## Running the App

### Development

Terminal 1 (Backend):
```bash
cd backend
python -m uvicorn app.main:app --reload
```

Terminal 2 (Frontend):
```bash
cd frontend  
npm run dev
```

Visit: http://localhost:3000

### API Documentation

Visit: http://localhost:8000/docs

## Usage

1. **Add Terms**: Use the dashboard to add keywords, hashtags, or tickers to monitor
2. **Configure Settings**: Toggle "Following Only" to restrict to accounts you follow
3. **Manual Run**: Click "Run Now" to immediately fetch and summarize tweets
4. **View Results**: Check the Results page for AI-generated summaries and top tweets
5. **Daily Auto-Run**: The scheduler runs daily at 8:00 AM UTC automatically

## Database Schema

### `monitored_terms`
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| keyword | TEXT | e.g. "$ORCL", "#AI" |
| restrict_following | BOOLEAN | true = only from followed accounts |
| active | BOOLEAN | toggle on/off |
| created_at | TIMESTAMP | creation time |

### `results`
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| keyword_id | INTEGER FK | references monitored_terms.id |
| tweets_raw | JSON | raw tweets data |
| summary | TEXT | AI-generated summary |
| created_at | TIMESTAMP | job run time |

## API Endpoints

- `GET /api/terms` - List monitored terms
- `POST /api/terms` - Add new term
- `PUT /api/terms/{id}` - Update term
- `DELETE /api/terms/{id}` - Remove term
- `GET /api/results` - List summaries
- `GET /api/results/{id}` - Get specific result
- `POST /api/run` - Manually trigger analysis

## Deployment

### Railway.app (Recommended)

1. Create new Railway project
2. Add Postgres database
3. Set environment variables in Railway dashboard
4. Update `DB_URL` to use Railway Postgres connection string
5. Deploy backend and frontend services

### Environment Variables for Production

```env
DB_URL=postgresql://user:password@host:port/database
X_API_KEY=your_x_api_key
X_API_SECRET=your_x_api_secret
X_BEARER_TOKEN=your_x_bearer_token
X_ACCESS_TOKEN=your_x_access_token
X_ACCESS_TOKEN_SECRET=your_x_access_token_secret
OPENAI_API_KEY=your_openai_key
# OR
ANTHROPIC_API_KEY=your_anthropic_key
```

## License

MIT