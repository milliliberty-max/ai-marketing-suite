# Instagram CrewAI Automation

AI-powered Instagram automation with **CrewAI agents** for content generation and **real-time auto-scheduled posting** via the Instagram Graph API.

## Features

- **AI Content Generation** — CrewAI agents (Content Strategist, Caption Writer, Hashtag Researcher, Schedule Optimizer) collaborate to create high-quality Instagram content
- **Auto-Scheduled Posting** — Schedule posts with exact date/time; the system auto-publishes via Instagram Graph API
- **Instant Posting** — Publish directly to Instagram with one click
- **Account Insights** — View follower count, recent post performance, and engagement metrics
- **Dashboard UI** — Clean web interface to manage everything
- **Carousel Support** — Schedule single image or multi-image carousel posts

## Prerequisites

- Python 3.10+
- Instagram Business/Creator account connected to a Facebook Page
- Meta Developer App with Instagram Graph API permissions
- OpenAI API key (for CrewAI agents)

## Setup

1. **Clone and install dependencies:**
   ```bash
   pip install -e .
   ```

2. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Run the application:**
   ```bash
   uvicorn src.app:app --host 0.0.0.0 --port 8000 --reload
   ```

4. **Open the dashboard:**
   Navigate to `http://localhost:8000`

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Dashboard UI |
| `/api/generate` | POST | Generate content with AI agents |
| `/api/schedule` | POST | Schedule a post |
| `/api/scheduled` | GET | List all scheduled posts |
| `/api/schedule/{id}` | DELETE | Cancel a scheduled post |
| `/api/post-now` | POST | Publish immediately |
| `/api/insights` | GET | Account insights |
| `/api/recent-posts` | GET | Recent posts with metrics |
| `/api/health` | GET | Health check |

## Environment Variables

| Variable | Description |
|---|---|
| `INSTAGRAM_ACCESS_TOKEN` | Long-lived Instagram Graph API token |
| `INSTAGRAM_BUSINESS_ACCOUNT_ID` | Instagram Business Account ID |
| `OPENAI_API_KEY` | OpenAI API key for CrewAI |

## Architecture

```
src/
├── app.py              # FastAPI application
├── models.py           # Pydantic request/response models
├── scheduler.py        # APScheduler-based auto-posting
├── agents/
│   └── content_crew.py # CrewAI agents and tasks
├── tools/
│   ├── instagram_api.py # Instagram Graph API client
│   └── crewai_tools.py  # Custom CrewAI tools
└── config/
    └── settings.py      # App settings
```
