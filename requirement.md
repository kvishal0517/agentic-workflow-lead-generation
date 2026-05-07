You are a Senior AI Engineer. Build a production-ready autonomous "Morning Lead Hunter" agent in Python.

GOAL: Every day at 08:00 IST, discover the TOP 10 GENUINE B2B leads matching my ICP, draft a personalized email per lead, and push the drafts to my Gmail Drafts folder for human review. Never send.

STRICT REQUIREMENTS:

1\. Stack: Python 3.11, LangGraph, Pydantic v2, Loguru, APScheduler, Playwright, BeautifulSoup, google-api-python-client, email-validator, dnspython, PyYAML, SQLite via SQLAlchemy.

2\. LLM: Ollama (default model llama3.1:8b) with optional Groq fallback via env switch. No paid APIs required.

3\. Folder structure exactly as specified in <FOLDER\_TREE>.

4\. ICP loaded from config/icp.yaml. Provide a complete sample ICP for an agency selling websites + AI automation.

5\. Pipeline nodes: discover enrich validate score draft push. Each node a pure function over a typed state dict.

6\. Discovery: build queries via LLM from ICP, run Google Custom Search (free) + Bing fallback, dedupe by domain, scrape top pages.

Enrichment: extract emails from contact pages + Hunter.io optional; identify decision maker (founder/CEO/marketing).

7\. 8. Validation: DNS + MX check, content-based "real business" check, ICP exclude filter, LLM authenticity check with evidence.

9\. Scoring: hybrid LLM (0-100) + rules; pick top 10.

10\. Drafting: per-lead personalization hook pain point proof point soft CTA; output Subject + HTML body; under 140 words.

11\. Gmail: OAuth setup script, create\_draft only (never send), tag with X-Lead-Ref header and creation timestamp.

12\. Scheduling: APScheduler cron 08:00 Asia/Kolkata + GitHub Actions workflow + Dockerfile with cron. 13. Persistence: SQLite tables for runs, leads, drafts, evidence; every decision auditable.

14\. Notifications: Slack webhook summary after each run.

15\. Tests: pytest with mocked search/Gmail; coverage ≥ 80%.

16\. Logging: structured JSON logs with run\_id, lead\_id, node, latency.

17\. Guardrails: rate limits, retries with backoff, dry-run mode, max 10 drafts/day cap.

18\. README with setup, OAuth steps, env vars, run commands, troubleshooting.



DELIVERABLES: full working code, .env.example, requirements.txt, Dockerfile, GitHub Actions workflow,

sample ICP, prompts, tests, README.

VERIFICATION: produce a one-shot demo command python scripts/run\_daily.py-dry-run that prints a table of 10 mock leads + previews drafts without touching Gmail. A second command-live executes the full pipeline and creates real drafts.

Do not skip any deliverable. Do not output placeholders. Provide complete code.

