# Sales Meeting Analysis

AI-powered meeting transcript analyzer that automatically classifies calls as **sales** or **technical**, generates structured reports, and emails them as branded HTML documents.

## How It Works

1. A meeting payload (transcript, metadata) is sent to the FastAPI endpoint
2. A LangChain agent classifies the meeting type and language from the transcript
3. Based on classification, the agent switches to a specialized prompt and model (GPT-5.4-mini for classification, GPT-5.4 for analysis)
4. A detailed structured report is generated and saved as a branded HTML file
5. The report is emailed to the configured recipient via SMTP

## Architecture

```
POST /  (FastAPI)
  -> format transcript
  -> LangChain Agent (create_agent + middleware)
       ├── Step 1: define_meeting_parameters (classify type + language)
       ├── Step 2: Middleware swaps prompt, model, and available tools
       └── Step 3: save_sales_analysis / save_technical_analysis
  -> send HTML report via email
```

### Middleware Pipeline

- **`dynamic_prompt`** — loads a meeting-type-specific prompt from `prompts/`
- **`dynamic_model_selection`** — uses GPT-5.4-mini for classification, GPT-5.4 for full analysis
- **`state_based_tool_selection`** — restricts available tools based on the detected meeting type

## Report Types

### Sales Report
Covers deal snapshot, 10-dimension scorecard, SPIN analysis, MEDDIC qualification, objection handling, missed questions, competitive intelligence, next actions, and a follow-up email draft.

### Technical Report
Covers technical snapshot, 7-dimension scorecard, what went well/wrong (with transcript quotes), missed technical questions, extracted requirements (functional, non-functional, constraints, assumptions), risks, open questions, next actions, and a follow-up message draft.

## Setup

### Prerequisites
- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager

### Install

```bash
uv sync
```

### Environment Variables

Create a `.env` file:

```env
OPENAI_API_KEY=your-openai-key

# Optional: LangSmith tracing
LANGSMITH_API_KEY=your-langsmith-key
LANGSMITH_TRACING=true

# SMTP for email delivery
SMTP_HOST=smtp.example.com
SMTP_PORT=465
SMTP_USER=your-email@example.com
SMTP_PASS=your-app-password
```

### Run

```bash
uv run uvicorn main:app --reload
```

### API Usage

```bash
curl -X POST http://localhost:8000/ \
  -H "Content-Type: application/json" \
  -d '{
    "attendees": ["Alice", "Bob"],
    "createdAt": 1745395200,
    "duration": 45.0,
    "meetingId": "abc-123",
    "title": "Discovery Call",
    "transcript": [
      {"speaker": "Alice", "text": "Let me walk you through our solution..."},
      {"speaker": "Bob", "text": "What about pricing?"}
    ],
    "type": "meeting",
    "videoId": "vid-456"
  }'
```

## Project Structure

```
├── main.py           # FastAPI app, endpoint handler
├── agents.py         # LangChain agent setup with middleware
├── tools.py          # Agent tools (classify, save sales/technical reports)
├── middleware.py      # Dynamic prompt, model, and tool selection
├── schemas.py        # Pydantic models for payloads, reports, and state
├── utils.py          # HTML report generation (sales + technical)
├── transcript.py     # Transcript formatting
├── email_sender.py   # SMTP email sender
├── prompts/          # Meeting-type-specific system prompts
│   ├── sales_prompt.md
│   └── technical_prompt.md
├── reports/          # Generated HTML reports (gitignored)
└── pyproject.toml    # Dependencies and project metadata
```

## Tech Stack

- **FastAPI** — HTTP API
- **LangChain** — Agent framework with middleware, tools, and structured output
- **LangGraph** — In-memory checkpointer for agent state
- **OpenAI GPT-5.4** — LLM for analysis
- **Pydantic** — Schema validation for payloads and reports
