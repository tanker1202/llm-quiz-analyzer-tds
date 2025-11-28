# Useful Commands Reference

## Quick Commands

### Setup & Installation

```bash
# Clone repository
git clone https://github.com/your-username/llm-analysis-quiz.git
cd llm-analysis-quiz

# Quick start (Linux/Mac)
./run.sh

# Manual setup
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium

# Configure
cp .env.example .env
nano .env  # or use your favorite editor
```

### Running the Application

```bash
# Method 1: Using run.sh
./run.sh

# Method 2: Direct Python
python app.py

# Method 3: Using uvicorn
uvicorn app:app --host 0.0.0.0 --port 8000

# Method 4: With auto-reload (development)
uvicorn app:app --reload

# Method 5: Production mode
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

### Testing

```bash
# Run system tests
python test_setup.py

# Test health endpoint
curl http://localhost:8000/health

# Test with invalid secret (should return 403)
curl -X POST http://localhost:8000/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","secret":"wrong","url":"http://example.com"}'

# Test with demo quiz
curl -X POST http://localhost:8000/ \
  -H "Content-Type: application/json" \
  -d '{
    "email":"your-email@example.com",
    "secret":"your-secret",
    "url":"https://tds-llm-analysis.s-anand.net/demo"
  }'
```

### Docker Commands

```bash
# Build image
docker build -t quiz-solver .

# Run container
docker run -p 8000:8080 --env-file .env quiz-solver

# Using Docker Compose
docker-compose up -d
docker-compose logs -f
docker-compose down

# Rebuild and run
docker-compose up --build
```

### Git Commands

```bash
# Initialize repository
git init
git add .
git commit -m "Initial commit"

# Connect to GitHub
git remote add origin https://github.com/your-username/llm-analysis-quiz.git
git branch -M main
git push -u origin main

# Update repository
git add .
git commit -m "Update code"
git push

# Check status
git status
git log --oneline
```

## Deployment Commands

### Heroku

```bash
# Install Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# Login
heroku login

# Create app
heroku create your-app-name

# Add buildpacks
heroku buildpacks:add heroku/python
heroku buildpacks:add https://github.com/mxschmitt/heroku-playwright-buildpack.git

# Set environment variables
heroku config:set STUDENT_EMAIL="your-email@example.com"
heroku config:set STUDENT_SECRET="your-secret"
heroku config:set ANTHROPIC_API_KEY="your-api-key"
heroku config:set DEFAULT_LLM_PROVIDER="anthropic"

# Deploy
git push heroku main

# View logs
heroku logs --tail

# Open app
heroku open

# Restart
heroku restart
```

### AWS EC2

```bash
# SSH into instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Install dependencies
sudo apt update
sudo apt install -y python3-pip python3-venv nginx

# Setup project
cd /home/ubuntu
git clone https://github.com/your-username/llm-analysis-quiz.git
cd llm-analysis-quiz
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
playwright install-deps

# Configure environment
cp .env.example .env
nano .env

# Create systemd service
sudo nano /etc/systemd/system/quiz-solver.service
# Paste service configuration

# Start service
sudo systemctl daemon-reload
sudo systemctl enable quiz-solver
sudo systemctl start quiz-solver
sudo systemctl status quiz-solver

# View logs
sudo journalctl -u quiz-solver -f

# Restart service
sudo systemctl restart quiz-solver

# Stop service
sudo systemctl stop quiz-solver
```

### Google Cloud Run

```bash
# Set project
gcloud config set project YOUR_PROJECT_ID

# Build and push
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/quiz-solver

# Deploy
gcloud run deploy quiz-solver \
  --image gcr.io/YOUR_PROJECT_ID/quiz-solver \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars STUDENT_EMAIL=your-email@example.com,STUDENT_SECRET=your-secret,ANTHROPIC_API_KEY=your-api-key,DEFAULT_LLM_PROVIDER=anthropic \
  --memory 2Gi \
  --timeout 300

# View logs
gcloud run services logs read quiz-solver --limit 50

# Update service
gcloud run services update quiz-solver \
  --update-env-vars NEW_VAR=value
```

## Troubleshooting Commands

### Check Dependencies

```bash
# Verify Python version
python --version

# Check installed packages
pip list

# Verify Playwright
playwright --version

# Check browser installation
playwright show-browsers

# Test httpx
python -c "import httpx; print(httpx.__version__)"

# Test all imports
python -c "import fastapi, uvicorn, playwright, httpx; print('All imports OK')"
```

### Debug Issues

```bash
# Run with debug logging
export LOG_LEVEL=DEBUG
python app.py

# Test browser manually
python -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto('https://example.com')
    print(page.title())
    browser.close()
"

# Test LLM connection
python -c "
import httpx
import os
response = httpx.post(
    'https://api.anthropic.com/v1/messages',
    headers={
        'x-api-key': os.getenv('ANTHROPIC_API_KEY'),
        'anthropic-version': '2023-06-01',
        'content-type': 'application/json'
    },
    json={
        'model': 'claude-sonnet-4-20250514',
        'max_tokens': 100,
        'messages': [{'role': 'user', 'content': 'Hello'}]
    }
)
print(response.status_code)
print(response.json())
"
```

### System Monitoring

```bash
# Check running processes
ps aux | grep python

# Check port usage
lsof -i :8000
netstat -tuln | grep 8000

# Monitor resource usage
top
htop

# Check disk space
df -h

# Check memory
free -h

# View system logs
tail -f /var/log/syslog

# Monitor network
nethogs
iftop
```

### Cleanup Commands

```bash
# Stop all Python processes
pkill -f "python app.py"

# Remove virtual environment
rm -rf venv

# Clean Python cache
find . -type d -name __pycache__ -exec rm -r {} +
find . -type f -name "*.pyc" -delete

# Clean Docker
docker system prune -a
docker volume prune

# Reset to clean state
git clean -fdx
```

## Development Commands

### Code Quality

```bash
# Format code with black
pip install black
black .

# Lint with flake8
pip install flake8
flake8 .

# Type checking with mypy
pip install mypy
mypy app.py

# Security check
pip install bandit
bandit -r .
```

### Environment Management

```bash
# Export environment variables
export STUDENT_EMAIL="your-email@example.com"
export STUDENT_SECRET="your-secret"
export ANTHROPIC_API_KEY="your-api-key"

# Load from .env file
set -a
source .env
set +a

# View all environment variables
env | grep STUDENT
env | grep API_KEY

# Clear environment variable
unset STUDENT_EMAIL
```

### File Operations

```bash
# Find all Python files
find . -name "*.py"

# Count lines of code
find . -name "*.py" -exec wc -l {} + | tail -1

# Search in files
grep -r "httpx" .
grep -r "TODO" . --include="*.py"

# File permissions
chmod +x run.sh
chmod 644 *.py
```

## Useful One-Liners

```bash
# Quick test endpoint
curl -s http://localhost:8000/health | python -m json.tool

# Watch logs in real-time
tail -f logs/*.log

# Count successful vs failed requests (from logs)
grep "correct" logs/app.log | wc -l

# Get external IP
curl ifconfig.me

# Test if port is accessible from outside
nc -zv your-domain.com 8000

# Generate random secret
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Measure response time
time curl -X POST http://localhost:8000/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test","secret":"test","url":"http://x.com"}'

# Monitor API usage (Anthropic)
# Check your dashboard at: https://console.anthropic.com/

# Monitor API usage (OpenAI)
# Check your dashboard at: https://platform.openai.com/usage
```

## Emergency Commands

### Quick Restart

```bash
# Kill and restart
pkill -f "uvicorn" && python app.py &

# Using systemd
sudo systemctl restart quiz-solver

# Docker
docker-compose restart

# Heroku
heroku restart
```

### Rollback

```bash
# Git rollback
git log --oneline
git reset --hard <commit-hash>
git push -f origin main

# Heroku rollback
heroku releases
heroku rollback v<number>
```

### Backup

```bash
# Backup .env
cp .env .env.backup

# Backup entire project
tar -czf quiz-solver-backup-$(date +%Y%m%d).tar.gz .

# Restore from backup
tar -xzf quiz-solver-backup-20251128.tar.gz
```

## Monitoring Commands

### During Evaluation

```bash
# Watch logs live
tail -f /var/log/quiz-solver.log

# Monitor HTTP requests
tcpdump -i any -A 'port 8000'

# Check system load
uptime
w

# Monitor specific process
watch -n 1 'ps aux | grep python'

# Count requests per minute
watch -n 60 'grep "Received valid quiz request" logs/app.log | wc -l'
```

---

## Command Aliases (Add to ~/.bashrc or ~/.zshrc)

```bash
# Add these to your shell config for quick access

alias quiz-start="cd ~/llm-analysis-quiz && source venv/bin/activate && python app.py"
alias quiz-test="cd ~/llm-analysis-quiz && source venv/bin/activate && python test_setup.py"
alias quiz-logs="tail -f ~/llm-analysis-quiz/logs/*.log"
alias quiz-restart="pkill -f 'python app.py' && cd ~/llm-analysis-quiz && python app.py &"
```

---

**Pro Tip**: Create a `Makefile` for common commands:

```makefile
.PHONY: install test run deploy clean

install:
	python3 -m venv venv
	. venv/bin/activate && pip install -r requirements.txt
	playwright install chromium

test:
	. venv/bin/activate && python test_setup.py

run:
	. venv/bin/activate && python app.py

deploy:
	git push heroku main

clean:
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
```

Then use: `make install`, `make test`, `make run`, etc.
