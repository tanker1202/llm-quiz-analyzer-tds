# Project Structure

```
llm-analysis-quiz/
│
├── app.py                      # FastAPI main application
├── quiz_solver.py              # Quiz solving orchestrator
├── browser_handler.py          # Playwright browser management
├── llm_handler.py             # LLM API integration (httpx)
├── submission_handler.py      # Answer submission (httpx)
├── config.py                  # Configuration management
├── advanced_llm_handler.py    # Enhanced LLM handler (optional)
├── test_setup.py              # System validation tests
│
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
├── .env                      # Your actual config (not in git)
├── .gitignore               # Git ignore rules
│
├── Dockerfile               # Container build instructions
├── docker-compose.yml       # Docker Compose configuration
├── run.sh                   # Quick start script
│
├── README.md                # Main documentation
├── QUICKSTART.md           # Quick start guide
├── DEPLOYMENT.md           # Deployment instructions
├── STRUCTURE.md            # This file
└── LICENSE                 # MIT License
```

## Component Details

### Core Application Files

#### `app.py` - Main FastAPI Application
- **Purpose**: HTTP endpoint that receives quiz requests
- **Key Features**:
  - POST endpoint at `/` for quiz requests
  - Health check endpoint at `/health`
  - Secret validation
  - Async task spawning
  - Error handling (400, 403, 500)

- **Flow**:
  ```
  POST / → Validate secret → Spawn async task → Return 200
  ```

#### `quiz_solver.py` - Quiz Orchestrator
- **Purpose**: Manages the quiz-solving workflow
- **Key Features**:
  - Chain handling (multiple quizzes in sequence)
  - Time management (3-minute limit)
  - Retry logic
  - Component coordination

- **Flow**:
  ```
  Start → Fetch page → Analyze with LLM → Submit answer → 
  Get next URL → Repeat until done or timeout
  ```

#### `browser_handler.py` - Browser Management
- **Purpose**: Fetch and render JavaScript-based quiz pages
- **Key Features**:
  - Playwright integration
  - Headless browser operation
  - JavaScript execution
  - Text extraction

- **Technology**: Playwright + Chromium

#### `llm_handler.py` - LLM Integration
- **Purpose**: Interact with LLM APIs to solve quizzes
- **Key Features**:
  - Support for Anthropic Claude and OpenAI
  - Uses httpx for HTTP requests (as required)
  - Prompt engineering
  - JSON response parsing
  - Fallback extraction

- **Supported Models**:
  - Anthropic: claude-sonnet-4-20250514
  - OpenAI: gpt-4-turbo-preview

#### `submission_handler.py` - Answer Submission
- **Purpose**: Submit answers to quiz endpoints
- **Key Features**:
  - Uses httpx for HTTP requests (as required)
  - Payload validation
  - Size limits (1MB)
  - Response parsing

#### `config.py` - Configuration
- **Purpose**: Centralized configuration management
- **Environment Variables**:
  - `STUDENT_EMAIL`
  - `STUDENT_SECRET`
  - `ANTHROPIC_API_KEY`
  - `OPENAI_API_KEY`
  - `DEFAULT_LLM_PROVIDER`
  - `QUIZ_TIMEOUT`
  - `HEADLESS`

### Optional/Advanced Files

#### `advanced_llm_handler.py` - Enhanced LLM
- **Purpose**: More sophisticated quiz solving
- **Features**:
  - Multi-step reasoning
  - File download capability
  - Data processing
  - Enhanced prompting

#### `test_setup.py` - System Tests
- **Purpose**: Validate system configuration
- **Tests**:
  - Configuration loading
  - Browser functionality
  - LLM connectivity
  - Submission handler

### Deployment Files

#### `Dockerfile`
- Base image: `python:3.11-slim`
- Includes Playwright and Chromium
- Optimized for production

#### `docker-compose.yml`
- Single-service configuration
- Environment variable mapping
- Health checks
- Volume mounting

#### `run.sh`
- Automated setup script
- Dependency installation
- Testing before starting
- Server launch

### Documentation Files

#### `README.md`
- Comprehensive project overview
- Features and architecture
- Installation instructions
- Usage guide
- Troubleshooting

#### `QUICKSTART.md`
- 5-minute setup guide
- Essential configuration
- Testing steps
- Common issues

#### `DEPLOYMENT.md`
- Detailed deployment options
- Cloud platform guides
- Cost estimates
- Monitoring setup

## Data Flow

### 1. Request Reception
```
External POST → FastAPI app.py → Validate secret → OK
```

### 2. Quiz Processing
```
quiz_solver.py → browser_handler.py → Fetch quiz page
                ↓
         Extract content
                ↓
         llm_handler.py → Analyze quiz → Generate solution
                ↓
         submission_handler.py → Submit answer → Get result
```

### 3. Chain Handling
```
Result correct? → Get next URL → Repeat from step 2
     ↓
Result wrong? → Retry or skip to next URL
     ↓
No more URLs? → End chain
```

## Key Technologies

- **Web Framework**: FastAPI
- **HTTP Client**: httpx (for LLM API calls and submissions)
- **Browser**: Playwright + Chromium
- **LLM Providers**: Anthropic Claude, OpenAI GPT
- **Async**: Python asyncio
- **Logging**: Python logging module

## Design Decisions

### Why httpx?
- Requirement specified in project description
- Modern async HTTP client
- Better than requests for async operations
- Used for both LLM API calls and quiz submissions

### Why Playwright?
- Handles JavaScript-rendered pages
- More reliable than simple HTTP requests
- Can wait for DOM elements
- Better than Selenium for this use case

### Why FastAPI?
- Modern async web framework
- Fast and efficient
- Built-in validation with Pydantic
- Easy to deploy

### Async vs Sync?
- Async for better performance
- Non-blocking I/O for HTTP requests
- Can handle multiple operations concurrently
- Better resource utilization

## Extension Points

Want to extend the project? Here are some ideas:

### 1. Add More LLM Providers
```python
# In llm_handler.py
async def _solve_with_gemini(self, quiz_content, quiz_url):
    # Implement Google Gemini integration
    pass
```

### 2. Add Caching
```python
from functools import lru_cache

@lru_cache(maxsize=100)
async def solve_quiz(self, quiz_content, quiz_url):
    # Cache LLM responses for similar questions
    pass
```

### 3. Add Database Logging
```python
# Track all quiz attempts
async def log_quiz_attempt(self, quiz_url, answer, result):
    # Save to database
    pass
```

### 4. Add Metrics
```python
from prometheus_client import Counter, Histogram

quiz_counter = Counter('quizzes_solved', 'Number of quizzes solved')
solve_time = Histogram('solve_duration', 'Time to solve quiz')
```

## Security Considerations

1. **Environment Variables**: Never commit `.env`
2. **API Keys**: Rotate regularly
3. **Input Validation**: All user inputs are validated
4. **Secret Verification**: Every request checks secret
5. **HTTPS**: Use in production
6. **Rate Limiting**: Consider adding for production

## Performance Optimization

1. **Connection Pooling**: httpx reuses connections
2. **Browser Reuse**: Single browser instance
3. **Async Operations**: Non-blocking I/O
4. **Timeout Management**: Prevents hanging
5. **Resource Cleanup**: Proper async cleanup

## Monitoring

### What to Monitor

1. **Request Rate**: Requests per minute
2. **Success Rate**: Correct vs incorrect answers
3. **Response Time**: End-to-end latency
4. **LLM Performance**: API response times
5. **Error Rate**: Failed requests
6. **Resource Usage**: CPU, memory, disk

### Log Locations

- **Development**: Console output
- **Production**: 
  - systemd: `journalctl -u quiz-solver`
  - Docker: `docker logs <container>`
  - Cloud: Platform-specific logging

## Troubleshooting Guide

### Common Issues

1. **Import Errors**: Check virtual environment activation
2. **Browser Errors**: Reinstall Playwright browsers
3. **API Errors**: Verify API keys and quotas
4. **Timeout Errors**: Check network and increase timeouts
5. **JSON Parse Errors**: Review LLM response format

### Debug Mode

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

When adding new features:

1. Follow existing code structure
2. Add logging statements
3. Update documentation
4. Test thoroughly
5. Consider edge cases

## License

MIT License - See LICENSE file
