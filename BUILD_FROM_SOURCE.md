<!--
Comprehensive build guide for AI Tech Daily Learner project.
This file contains instructions, env vars, prompts, Notion schema, CI steps,
and a minimal scaffold so another AI or developer can reproduce the project from scratch.
-->

# BUILD_FROM_SOURCE — AI Tech Daily Learner

Purpose
- A single, copy-pasteable guide to rebuild the "AI Tech Daily Learner" (Tech-only) project from scratch.
- Includes environment variables, dependencies, Notion schema, worker prompts and JSON schemas, CI/workflow, and a minimal file scaffold.

Prerequisites
- Python 3.10+ (recommended 3.11 for future compatibility)  
- Git and a GitHub account (for Actions)  
- A Notion account and an Internal Integration (integration token)  
- A Google Gemini (Generative) API key (from AI Studio / Google Cloud)

Quick summary (commands)

```bash
# clone and prepare
git clone <your-fork-url>
cd AI_Tech_Daily_Learner
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# macOS / Linux
# source .venv/bin/activate

# install worker deps
pip install -r worker-requirements.txt

# set environment variables (example)
export GEMINI_API_KEY="your_key_here"
export NOTION_TOKEN="secret_notion_token"
export NOTION_DATABASE_ID="your_database_id"
export GEMINI_MODEL="models/gemini-2.5-flash"

# run locally
python main.py
```

Environment variables (required & optional)
- Required:
  - `GEMINI_API_KEY` — Google Gemini API key (used for Tech worker).  
  - `NOTION_TOKEN` — Notion integration token (Internal Integration).  
  - `NOTION_DATABASE_ID` — Notion database id to write pages to.
- Optional:
  - `GEMINI_MODEL` — model name to use (defaults to a sensible model in code).  
  - `STOCK_CODES` — comma-separated stock symbols (if stock worker enabled).  
  - `RUN_ONLY` — optional ("Tech") to only run Tech worker from CI.

Dependencies
- The project uses a split dependency approach:
  - `requirements.txt` — minimal dependencies for web UI / Vercel.  
  - `worker-requirements.txt` — full dependencies used by `main.py`. Typical items:
    - requests
    - beautifulsoup4
    - google-generativeai (or prefer `google.genai` for migration)
    - yfinance (optional, if stocks used)

Notion Database schema (table view recommended)
Ensure the database has the exact property names and types below:

| Property Name | Type | Notes |
|---|---:|---|
| `Title` | Title | Primary title |
| `URL` | URL | Article or pseudo-URL |
| `Summary` | Rich Text | The bilingual summary block |
| `Keywords` | Multi-select | Bilingual keywords (term · translation) |
| `Date` | Date | Run date |
| `Score` | Number | 1–5 |
| `Category` | Select | Options: `Tech` |
| `Sentiment` | Select | (Optional) Pay attention only if Stock is used |

Workers overview (Tech-only)
- Worker: Tech News
  - Source: Hacker News Top Stories (via official API)
  - Behavior: fetch top story IDs (configurable MAX_ARTICLES), fetch each article body, generate a bilingual learning summary using Gemini, push to Notion.
  - Key code path: `worker_tech()` → `summarize_tech_article()`

ArticlePayload (output JSON schema)
```json
{
  "title": "string",
  "url": "string",
  "summary_points": ["string", "..."],   // Chinese bullet points
  "keywords": [{"term_en":"string","term_zh":"string"}],
  "one_liner": "string",                // English one-liner
  "score": 1                             // integer 1-5
}
```

Prompt templates and expected wrapping
- To make model outputs robustly parseable, prompts must instruct the model to wrap JSON between exact markers:

Example (Tech summary prompt):
```
You are an assistant who summarizes technical articles for bilingual learners.
Return ONLY valid JSON. Wrap the entire JSON output between markers exactly as
<<<JSON_START>>>
{ ... JSON per schema ... }
<<<JSON_END>>>
Do not add other text outside the markers.
Keep wording beginner-friendly.
```

Parsing rules
- First search for `<<<JSON_START>>>` and `<<<JSON_END>>>`. If both found, extract the text between them and parse JSON.  
- If only `JSON_START` present, attempt balanced-brace extraction starting from the first `{`.  
- Fallback sanitizations: remove trailing commas, strip markdown fences, and attempt JSON parse. If parse fails, store fallback text and log full response for debugging.

Diagnostics & logging
- Log the full Gemini response object (candidates, each part length, finish_reason) to CI logs to debug empty/filtered responses.  
- Record a truncated `raw_text` preview (first N characters) and, on error, capture a larger preview (up to 4k chars) in logs.

CI / GitHub Actions
- Workflow (`.github/workflows/daily_run.yml`) should:
  - Checkout repo, set up Python, install `worker-requirements.txt`, and run `python main.py`.
  - Provide required secrets as env:
    - `GEMINI_API_KEY`, `NOTION_TOKEN`, `NOTION_DATABASE_ID`, optional `GEMINI_MODEL`
  - Optionally set `RUN_ONLY: "Tech"` when you only want Tech worker.

Minimal file scaffold (files to create in a new repo)
- main.py (core worker script) — orchestrates workers and performs Notion writes. Must include:
  - require_env_var() checks
  - Hacker News fetcher
  - fetch_article_content(url)
  - summarize_tech_article(model, title, text)
  - push_to_notion(token, db_id, ArticlePayload)
  - run() main entry
- worker-requirements.txt
- .github/workflows/daily_run.yml
- scripts/list_models.py (helper to list available models)
- README.md / README.zh-CN.md / BUILD_FROM_SOURCE.md

Minimal main.py skeleton (example)
```python
import os, requests, json, logging
from google import genai  # recommended; or google.generativeai for legacy

def require_env_var(name):
    v=os.getenv(name)
    if not v: raise RuntimeError(...)
    return v

def fetch_top_story_ids():
    # call HN topstories API
    pass

def fetch_article_content(url):
    # requests.get(url, headers={'User-Agent':...})
    pass

def summarize_tech_article(model, title, article_text):
    prompt = "... use <<<JSON_START>>> markers ..."
    resp = model.generate_content([prompt, "Article body:", article_text], ...)
    # extract between markers, parse, return ArticlePayload-like dict
    pass

def push_to_notion(token, db_id, payload):
    # build properties and POST to Notion /pages
    pass

if __name__ == '__main__':
    run()
```

Testing and validation
- Local smoke test: run `python main.py` with `MAX_ARTICLES=1` and verify Notion database contains one new Tech entry.  
- CI smoke test: create a test GitHub Actions run that sets secrets to staging/test tokens and asserts the exit code is 0.  
- If Gemini returns empty or truncated responses: consult CI logs for `finish_reason` (MAX_TOKENS), and try:
  - increase `max_output_tokens`,
  - shorten prompt output (fewer phrases/keywords),
  - split generation into multiple calls.

Migration note (recommended)
- Replace `google.generativeai` with `google.genai`:
  - New package provides updated client & response shapes.
  - Adjust code where `model.generate_content()` is called — follow `google.genai` docs.

Troubleshooting checklist
- If you see `404 model ... not found`: run `scripts/list_models.py` with your key and pick a supported model name.  
- If you see `finish_reason=MAX_TOKENS`: increase tokens or shorten output.  
- If you see empty textual parts: inspect candidates/parts in logs (we log them) and migrate to `google.genai` if needed.

Deliverables this guide should produce
1. `BUILD_FROM_SOURCE.md` (this file)  
2. `main.py` minimal scaffold (copy from skeleton)  
3. `worker-requirements.txt` with all dependencies  
4. `.github/workflows/daily_run.yml` CI config

Usage: hand this file + repository contents to another AI or developer; they can follow sections:
- "Quick summary" to set up env and run;  
- "Notion Database schema" to create the DB;  
- "Prompt templates" to seed model generation;  
- "Scaffold" to recreate minimal runnable code.

----
If you want, I can now:
- create `BUILD.md` file in the repo (this same content); and/or  
- create `main_minimal.py` with the skeleton filled (I can implement the minimum runnable tech worker that uses the prompts above).  
Reply "create files" to have me add them to the repo, or "I will do it" to keep this MD only.


