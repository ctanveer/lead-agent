# Lead scoring agent

FastAPI service: POST /leads -> enrich -> Claude (claude-haiku-5-5, forced `record_score` tool) scores 5 rubric
criteria -> code clamps + sums -> tier (hot >= 70, warm 40-69, cold < 40) -> SQLite upsert -> Slack alert for hot.
Free-email leads are cold without a Claude call; any scoring failure is stored as `review` and alerted.

## Run
    python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
    cp .env.example .env    # fill in ANTHROPIC_API_KEY, SLACK_WEBHOOK_URL, LEAD_API_KEY
    uvicorn app:app --reload
    python -m pytest -q     # offline tests, Claude mocked
    python eval.py          # live: agreement vs labeled_leads.csv (replace with your 20 labeled leads)

Before going live: replace the <PLACEHOLDERS> in scoring.SYSTEM with your ICP, and the enrichment URL/fields in enrich.py.
Warm/nurture list: `SELECT * FROM leads WHERE tier='warm' AND status='new'`.
