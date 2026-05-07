# 🌅 Morning Lead Hunter

An autonomous B2B lead generation agent that discovers, enriches, validates, scores, and drafts personalized emails every morning at 08:00 IST.

## 🚀 Features
- **LangGraph Orchestration**: Robust multi-node pipeline.
- **LLM Integration**: Uses Ollama (local) or Groq (cloud) for intelligence.
- **Gmail Automation**: Creates personalized drafts for human review.
- **Persistence**: SQLite database for auditability.
- **Dockerized**: Easy deployment with cron scheduling.

## 🛠️ Setup

### 1. Prerequisites
- Python 3.11+
- Ollama (with `llama3.1:8b` model)
- Google Cloud Project (for Gmail API & Custom Search)

### 2. Install Dependencies
```bash
pip install -r requirements.txt
playwright install --with-deps chromium
```

### 3. Google OAuth Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Enable **Gmail API** and **Custom Search API**.
3. Create **OAuth 2.0 Client ID** (Desktop Application).
4. Download the `client_secret.json` or copy the credentials to `.env`.
5. Run the setup script:
   ```bash
   python scripts/setup_oauth.py
   ```
   Follow the browser instructions to authenticate. This creates `token.json`.

### 4. Configuration
Copy `.env.example` to `.env` and fill in the details.
Modify `config/icp.yaml` to match your target audience.

## 🏃 Usage

### Dry Run (Mock Mode)
Test the pipeline without hitting Google Search APIs or creating real Gmail drafts:
```bash
python scripts/run_daily.py --dry-run
```

### Live Run
Execute the full pipeline:
```bash
python scripts/run_daily.py --live
```

### Scheduled Mode (Docker)
```bash
docker build -t lead-hunter .
docker run --env-file .env lead-hunter
```

## 📂 Folder Structure
```
.
├── config/             # ICP and App settings
├── src/
│   ├── agents/         # LangGraph logic and nodes
│   ├── database/       # SQLAlchemy models
│   ├── utils/          # Search, Gmail, LLM helpers
│   └── main.py         # App Entrypoint (Scheduler)
├── scripts/            # CLI Tools (OAuth, Manual Run)
├── tests/              # Pytest suite
└── Dockerfile          # Container config
```

## 🧪 Testing
```bash
pytest tests/
```

## 📜 License
MIT
