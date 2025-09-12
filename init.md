# 📄 init.md – Project Brief for Coding Assistant

## Project Goal
Build a **lightweight personal web app** to track keywords, tickers, and hashtags on **X.com (Twitter)** using my **X Premium API quota**.  
The app should run on a daily schedule, summarize tweets with an LLM, and present results in a simple web dashboard.  

---

## Key Features
- Input keywords/hashtags/tickers to monitor (e.g., `$ORCL`, `#AI`).  
- Toggle: restrict results only to accounts I follow.  
- Daily scheduled fetch from X API (not too frequent to save quota).  
- Summarize results with an LLM (OpenAI/Claude).  
- Display latest summaries + top tweets in a web dashboard.  
- Backend API for configuration and results.  
- SQLite for local dev, Postgres for production (Railway.app).  

---

## Tech Stack
- **Backend:** Python (Flask or FastAPI)  
- **Frontend:** React + Tailwind (or Flask/Jinja templates if simpler)  
- **Database:** SQLite (dev), Postgres (prod)  
- **Scheduler:** APScheduler (in backend) or cron job  
- **Integrations:**  
  - X API v2 (`search_recent_tweets`)  
  - DeepSeek v3.1 API for summarization  

---

## Database Schema

### `monitored_terms`
| Column               | Type       | Notes |
|-----------------------|------------|-------|
| `id`                 | INTEGER PK | Auto-increment |
| `keyword`            | TEXT       | e.g. "$ORCL", "#AI" |
| `restrict_following` | BOOLEAN    | true = only from accounts user follows |
| `active`             | BOOLEAN    | toggle on/off |

### `results`
| Column        | Type       | Notes |
|---------------|------------|-------|
| `id`          | INTEGER PK | Auto-increment |
| `keyword_id`  | INTEGER FK | references `monitored_terms.id` |
| `tweets_raw`  | JSON/TEXT  | raw tweets data |
| `summary`     | TEXT       | AI-generated summary |
| `created_at`  | TIMESTAMP  | job run time |

---

## Backend API Endpoints

- `GET /api/terms` → list monitored terms  
- `POST /api/terms` → add new term (`keyword`, `restrict_following`)  
- `PUT /api/terms/{id}` → update term (toggle active/following)  
- `DELETE /api/terms/{id}` → remove term  

- `GET /api/results` → list summaries (latest per term)  
- `GET /api/results/{id}` → show summary + tweets for one run  

- `POST /api/run` → manually trigger fetch/summarize  

---

## Daily Job Flow
1. Load all active terms.  
2. For each:  
   - Build query string.  
   - If restrict_following = true → add filter for following accounts.  
   - Fetch ~50 tweets with `search_recent_tweets`.  
   - Summarize with LLM using this format:  

   ```
   Summarize the following tweets into:
   1. Main themes
   2. Positive sentiment
   3. Negative sentiment
   4. Notable insights
   ```
3. Save raw tweets + summary in DB.  

---

## Frontend UI
- **Dashboard**: list of monitored terms with toggles and “Run Now” button.  
- **Results View**: show summaries, expand to see top 5 tweets (with links).  
- **Add/Edit Term**: input keyword/hashtag, checkbox for restrict-to-following.  

---

## Deployment Notes
- **SQLite (dev):** use `sqlite:///local.db` locally.  
- **Postgres (prod):** Railway.app Postgres plugin recommended.  
- Use SQLAlchemy ORM so schema works across both.  
- Environment variables (`.env`):  
  ```
  X_API_KEY=xxxx
  X_API_SECRET=xxxx
  X_BEARER_TOKEN=xxxx
  X_ACCESS_TOKEN=xxxx
  X_ACCESS_TOKEN_SECRET=xxxx
  DEEPSEEK_API_KEY=xxxx
  DEEPSEEK_MODEL=deepseek-chat
  DB_URL=sqlite:///local.db   # for dev
  ```
- In Railway, update `DB_URL` with the Postgres connection string.  
- Run migrations with Alembic/Flask-Migrate on deploy.  

---

## Future Enhancements
- Email digests of summaries.  
- Sentiment charts.  
- Multi-user OAuth (each user uses own X quota).  
- Export summaries to CSV/PDF.  

---

✅ Deliverable:  
- Working backend (Flask/FastAPI) + frontend (React/Tailwind).  
- SQLite for local testing, Postgres for Railway deployment.  
- Scheduler runs once/day, plus manual run endpoint.  
- Dashboard to manage keywords and view results.  
