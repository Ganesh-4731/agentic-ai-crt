# SkyStride AI — Hybrid Telegram Travel Bot

> A hyper-personalised trip blueprint generator powered by Telegram, Python, n8n, Groq LLM, OpenWeatherMap, and OpenRouteService.

---

## Architecture

```
User ↔ Telegram
         ↓ ↑
   [Python Bot — lightweight]
   • Multi-step conversation (collects 6 inputs)
   • On final input: POST all params to n8n webhook
   • Waits for n8n response (the blueprint text)
   • Sends blueprint back to Telegram user
         ↓ ↑
   [n8n Workflow — heavy lifting]
   • Receives trip params via Webhook node
   • HTTP node → OpenWeatherMap (origin weather)
   • HTTP node → OpenWeatherMap (destination weather)
   • HTTP node → OpenRouteService (geocode origin)
   • HTTP node → OpenRouteService (geocode destination)
   • HTTP node → OpenRouteService (route stops)
   • Code node → assemble full prompt
   • HTTP node → Groq API (generate blueprint)
   • Respond to Webhook → return blueprint JSON to Python
```

Full data flow:

```
User → Telegram → Python Bot → n8n Webhook
  → [OpenWeatherMap (origin)] → [OpenWeatherMap (destination)]
  → [OpenRouteService geocode] → [OpenRouteService route]
  → [Groq LLM llama-3.3-70b-versatile]
  → n8n Respond to Webhook → Python Bot → Telegram → User
```

---

## Prerequisites

- Python 3.11+
- n8n running locally at `localhost:5678` (self-hosted)
- 4 free API keys (see below)

---

## How to Get API Keys

| Service | URL | Notes |
|---|---|---|
| **Telegram Bot** | [@BotFather](https://t.me/BotFather) → `/newbot` | Free |
| **Groq** | https://console.groq.com | Free tier, fast LLM inference |
| **OpenWeatherMap** | https://openweathermap.org/api | Free tier (1000 calls/day) |
| **OpenRouteService** | https://openrouteservice.org | Free tier (2000 calls/day) |

---

## Setup Steps

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Then edit `.env` and fill in all five values:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
N8N_WEBHOOK_URL=http://localhost:5678/webhook/skystride-blueprint
GROQ_API_KEY=your_groq_api_key
OPENWEATHERMAP_API_KEY=your_openweathermap_api_key
ORS_API_KEY=your_openrouteservice_api_key
```

### 3. Open n8n

Navigate to `http://localhost:5678` in your browser.

### 4. Import the workflow

- Go to **Settings → Import Workflow** (or use the **+** button on the Workflows page → **Import from File**)
- Select `n8n/skystride_workflow.json`
- Click **Import**

### 5. Set n8n environment variables

In n8n, go to **Settings → Environment Variables** and add:

| Key | Value |
|---|---|
| `GROQ_API_KEY` | your Groq key |
| `OPENWEATHERMAP_API_KEY` | your OWM key |
| `ORS_API_KEY` | your ORS key |

> ⚠️ n8n accesses these via `$env.VARIABLE_NAME` inside nodes. They must be set in n8n's own environment, not just in your `.env` file.

### 6. Activate the workflow

In n8n, open the imported **SkyStride AI Blueprint Workflow** and toggle the **Active** switch to ON.

The webhook URL will become live at:
```
http://localhost:5678/webhook/skystride-blueprint
```

### 7. Run the bot

```bash
python main.py
# or
bash run.sh
```

### 8. Test it

Open Telegram, find your bot, and send `/start`. You'll be guided through 6 short questions. The full blueprint arrives in ~15–20 seconds.

---

## Project Structure

```
skystride/
├── main.py                        ← App entry point
├── bot/
│   ├── __init__.py
│   ├── handlers.py                ← ConversationHandler (6 steps)
│   └── webhook_client.py          ← httpx POST to n8n, returns blueprint
├── utils/
│   ├── __init__.py
│   ├── formatter.py               ← splits long blueprints for Telegram
│   └── logger.py                  ← console + file logging
├── n8n/
│   └── skystride_workflow.json    ← importable n8n workflow (10 nodes)
├── logs/                          ← auto-created at runtime
│   └── app.log
├── .env.example
├── .gitignore
├── requirements.txt
└── run.sh
```

---

## n8n Workflow Node Summary

| # | Node | Type | Purpose |
|---|---|---|---|
| 1 | Webhook | Trigger | Receives POST from Python |
| 2 | Get Origin Weather | HTTP Request | OWM forecast for origin |
| 3 | Get Destination Weather | HTTP Request | OWM forecast for destination |
| 4 | Geocode Origin | HTTP Request | ORS geocode → [lon, lat] |
| 5 | Geocode Destination | HTTP Request | ORS geocode → [lon, lat] |
| 6 | Get Route | HTTP Request | ORS driving route GeoJSON |
| 7 | Assemble Prompt | Code (JS) | Builds structured user message |
| 8 | Call Groq API | HTTP Request | LLM blueprint generation |
| 9 | Extract Blueprint | Code (JS) | Pulls text from Groq response |
| 10 | Respond to Webhook | Respond | Returns JSON to Python |

---

## Cost

**Entirely free for personal use.**

All APIs used have generous free tiers:
- Groq: free tier with llama-3.3-70b-versatile
- OpenWeatherMap: 1,000 API calls/day free
- OpenRouteService: 2,000 API calls/day free
- Telegram Bot API: free
- n8n self-hosted: free

---

## Troubleshooting

**Bot doesn't respond after "Generating blueprint..."**
- Check that n8n is running (`http://localhost:5678`)
- Check that the workflow is **Active** (toggle ON)
- Check n8n environment variables are set
- Check `logs/app.log` for error details

**n8n webhook returns 404**
- The workflow must be **Active** for the webhook to be live
- The path must match exactly: `skystride-blueprint`

**Weather data missing**
- Verify `OPENWEATHERMAP_API_KEY` is set in n8n Environment Variables
- Free tier activates ~2 hours after registration

**Route/geocode failing**
- Verify `ORS_API_KEY` is set in n8n Environment Variables
- Try more specific city names (e.g. "Mumbai, India" instead of "Mumbai")
