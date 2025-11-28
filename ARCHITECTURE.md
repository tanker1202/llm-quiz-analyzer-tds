# System Architecture

## High-Level Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         EVALUATION SERVER                        │
│                                                                   │
│  Sends POST request with quiz URL                               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ POST {email, secret, url}
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      YOUR ENDPOINT (FastAPI)                     │
│                         app.py:handle_quiz()                     │
│                                                                   │
│  1. Validate secret ────────────┐                               │
│                                  │                               │
│  2. Return HTTP 200             │                               │
│                                  │                               │
│  3. Spawn async task ───────────┼─────────────────────┐        │
└──────────────────────────────────┼─────────────────────┼────────┘
                                   │                     │
                   ┌───────────────┘                     │
                   │ Invalid secret                      │
                   │                                     │
                   ▼                                     ▼
          Return HTTP 403              ┌─────────────────────────────┐
                                       │    QuizSolver (async task)   │
                                       │    quiz_solver.py            │
                                       └──────────┬──────────────────┘
                                                  │
                     ┌────────────────────────────┼────────────────────────┐
                     │                            │                         │
                     ▼                            ▼                         ▼
          ┌──────────────────┐      ┌──────────────────────┐   ┌──────────────────┐
          │ BrowserHandler   │      │    LLMHandler        │   │SubmissionHandler │
          │ browser_handler  │      │   llm_handler.py     │   │ submission_hand  │
          │      .py         │      │   (uses httpx ⭐)    │   │   ler.py         │
          │                  │      │                      │   │ (uses httpx ⭐)  │
          └────────┬─────────┘      └──────────┬───────────┘   └────────┬─────────┘
                   │                           │                        │
                   │                           │                        │
    Step 1: Fetch quiz page      Step 2: Analyze with LLM   Step 3: Submit answer
                   │                           │                        │
                   ▼                           ▼                        ▼
          ┌──────────────────┐      ┌──────────────────────┐   ┌──────────────────┐
          │  Playwright      │      │  Anthropic API       │   │  Quiz Submit     │
          │  (Chromium)      │      │     or               │   │   Endpoint       │
          │                  │      │  OpenAI API          │   │                  │
          │  Renders JS      │      │                      │   │  Returns result  │
          │  Returns text    │      │  Returns solution    │   │  + next URL      │
          └──────────────────┘      └──────────────────────┘   └──────────────────┘
```

## Detailed Component Interaction

```
┌────────────────────────────────────────────────────────────────────┐
│                         QUIZ CHAIN FLOW                             │
└────────────────────────────────────────────────────────────────────┘

Quiz URL #1
    │
    ├──► BrowserHandler.fetch_quiz_page()
    │         │
    │         ├─► Launch Playwright
    │         ├─► Navigate to URL
    │         ├─► Wait for JavaScript
    │         └─► Extract text content
    │
    ├──► LLMHandler.solve_quiz()
    │         │
    │         ├─► Build comprehensive prompt
    │         ├─► Call LLM API via httpx
    │         │       │
    │         │       ├─► Anthropic: POST to /v1/messages
    │         │       │   OR
    │         │       └─► OpenAI: POST to /v1/chat/completions
    │         │
    │         ├─► Parse JSON response
    │         └─► Return {submit_url, answer}
    │
    ├──► SubmissionHandler.submit_answer()
    │         │
    │         ├─► Build JSON payload
    │         ├─► POST via httpx
    │         └─► Parse response
    │
    └──► Got next URL?
              │
              ├─► YES ──► Repeat with Quiz URL #2
              │
              └─► NO ──► Chain complete ✓


┌────────────────────────────────────────────────────────────────────┐
│                      ERROR HANDLING FLOW                            │
└────────────────────────────────────────────────────────────────────┘

Answer Wrong?
    │
    ├──► Within 3 min timeout?
    │         │
    │         ├─► YES ──► Retry current quiz
    │         │              │
    │         │              ├─► Correct? ──► Next URL
    │         │              │
    │         │              └─► Wrong? ──► Skip to next URL (if provided)
    │         │
    │         └─► NO ──► End chain (timeout)
    │
    └──► No next URL provided? ──► End chain
```

## Data Structures

```
┌────────────────────────────────────────────────────────────────────┐
│                         REQUEST/RESPONSE                            │
└────────────────────────────────────────────────────────────────────┘

Incoming Request:
{
    "email": "student@example.com",
    "secret": "unique-secret-123",
    "url": "https://example.com/quiz-834"
}

LLM Response:
{
    "submit_url": "https://example.com/submit",
    "answer": 12345,  // Can be: number, string, boolean, object, base64
    "reasoning": "Sum of values: 100+200+...",
    "data_sources": ["https://example.com/data.pdf"],
    "processing_steps": ["Download PDF", "Parse page 2", "Sum values"]
}

Submission Payload:
{
    "email": "student@example.com",
    "secret": "unique-secret-123",
    "url": "https://example.com/quiz-834",
    "answer": 12345
}

Submission Response (Success):
{
    "correct": true,
    "url": "https://example.com/quiz-942",  // Next quiz
    "reason": null
}

Submission Response (Failure):
{
    "correct": false,
    "url": "https://example.com/quiz-942",  // Optional next quiz
    "reason": "The sum is incorrect. Expected 54321."
}
```

## Component Dependencies

```
┌────────────────────────────────────────────────────────────────────┐
│                      DEPENDENCY GRAPH                               │
└────────────────────────────────────────────────────────────────────┘

app.py
  │
  ├──► FastAPI
  ├──► Pydantic
  └──► quiz_solver.py
          │
          ├──► browser_handler.py
          │       │
          │       ├──► Playwright
          │       └──► config.py
          │
          ├──► llm_handler.py
          │       │
          │       ├──► httpx ⭐ (for LLM API)
          │       └──► config.py
          │
          ├──► submission_handler.py
          │       │
          │       ├──► httpx ⭐ (for submissions)
          │       └──► config.py
          │
          └──► config.py
                  │
                  └──► python-dotenv
```

## File Organization

```
Project Root
│
├── Core Application
│   ├── app.py                    ◄── Entry point
│   ├── quiz_solver.py            ◄── Orchestrator
│   ├── browser_handler.py        ◄── Page fetching
│   ├── llm_handler.py           ◄── LLM calls (httpx)
│   ├── submission_handler.py    ◄── Answer submission (httpx)
│   └── config.py                ◄── Configuration
│
├── Optional/Advanced
│   ├── advanced_llm_handler.py  ◄── Enhanced solving
│   └── test_setup.py            ◄── System tests
│
├── Configuration
│   ├── requirements.txt         ◄── Dependencies
│   ├── .env.example            ◄── Config template
│   └── .gitignore              ◄── Git rules
│
├── Deployment
│   ├── Dockerfile              ◄── Container
│   ├── docker-compose.yml      ◄── Docker setup
│   └── run.sh                  ◄── Quick start
│
└── Documentation
    ├── README.md               ◄── Main guide
    ├── QUICKSTART.md           ◄── 5-min setup
    ├── DEPLOYMENT.md           ◄── Deploy guides
    ├── STRUCTURE.md            ◄── Architecture
    ├── PROJECT_SUMMARY.md      ◄── Overview
    ├── ARCHITECTURE.md         ◄── This file
    └── LICENSE                 ◄── MIT
```

## Technology Stack

```
┌────────────────────────────────────────────────────────────────────┐
│                         TECH STACK                                  │
└────────────────────────────────────────────────────────────────────┘

Layer              Technology           Purpose
─────────────────────────────────────────────────────────────────────
Web Framework      FastAPI              HTTP endpoint, async support
HTTP Client        httpx ⭐             LLM API calls, submissions
Browser            Playwright           JS rendering, page fetching
Browser Engine     Chromium             Headless browser
Data Validation    Pydantic             Request/response validation
Async Runtime      asyncio              Non-blocking I/O
LLM Providers      Anthropic Claude     Primary quiz solver
                   OpenAI GPT           Alternative solver
Config             python-dotenv        Environment variables
Logging            Python logging       Debug and monitoring
Containerization   Docker               Deployment packaging
```

## Key Design Patterns

```
┌────────────────────────────────────────────────────────────────────┐
│                      DESIGN PATTERNS                                │
└────────────────────────────────────────────────────────────────────┘

1. Dependency Injection
   Config → All handlers
   Centralizes configuration management

2. Strategy Pattern
   LLMHandler supports multiple providers (Anthropic, OpenAI)
   Switchable via config

3. Facade Pattern
   QuizSolver hides complexity of browser/LLM/submission

4. Async/Await Pattern
   Non-blocking I/O throughout
   Better resource utilization

5. Factory Pattern
   Browser/LLM/Submission handlers created by QuizSolver

6. Chain of Responsibility
   Quiz chain: URL1 → URL2 → URL3 → ...
```

## Scalability Considerations

```
Current Implementation:
- Single instance
- Sequential quiz solving
- One browser instance

Possible Enhancements:
- Multiple workers (Gunicorn)
- Parallel quiz processing
- Connection pooling (already in httpx)
- LLM response caching
- Distributed task queue (Celery)
```

## Security Model

```
┌────────────────────────────────────────────────────────────────────┐
│                      SECURITY LAYERS                                │
└────────────────────────────────────────────────────────────────────┘

1. Authentication
   └─► Secret validation (403 if wrong)

2. Input Validation
   └─► Pydantic models validate requests

3. Environment Variables
   └─► Secrets never in code

4. HTTPS
   └─► Encrypted transport (production)

5. Payload Size Limits
   └─► 1MB max submission

6. Timeout Protection
   └─► 3-minute hard limit
```

---

**Legend:**
- ⭐ = Key requirement (httpx usage)
- ◄── = Primary files
- └─► = Leads to / Results in
