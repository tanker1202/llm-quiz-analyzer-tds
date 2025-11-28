# Deployment Guide

## Quick Start Deployment

### Local Development

1. **Setup**:
```bash
# Clone repository
git clone <your-repo-url>
cd llm-analysis-quiz

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Configure environment
cp .env.example .env
# Edit .env with your credentials
```

2. **Run**:
```bash
python app.py
```

3. **Test**:
```bash
python test_setup.py
```

### Cloud Deployment Options

## Option 1: Heroku

1. **Install Heroku CLI**:
```bash
curl https://cli-assets.heroku.com/install.sh | sh
```

2. **Create Heroku app**:
```bash
heroku create your-app-name
```

3. **Add buildpacks**:
```bash
heroku buildpacks:add heroku/python
heroku buildpacks:add https://github.com/mxschmitt/heroku-playwright-buildpack.git
```

4. **Set environment variables**:
```bash
heroku config:set STUDENT_EMAIL="your-email@example.com"
heroku config:set STUDENT_SECRET="your-secret"
heroku config:set ANTHROPIC_API_KEY="your-api-key"
heroku config:set DEFAULT_LLM_PROVIDER="anthropic"
```

5. **Create Procfile**:
```bash
echo "web: uvicorn app:app --host 0.0.0.0 --port \$PORT" > Procfile
```

6. **Deploy**:
```bash
git add .
git commit -m "Initial deployment"
git push heroku main
```

7. **Your endpoint**: `https://your-app-name.herokuapp.com/`

## Option 2: AWS EC2

1. **Launch EC2 instance** (Ubuntu 22.04, t2.medium or larger)

2. **SSH into instance**:
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

3. **Install dependencies**:
```bash
sudo apt update
sudo apt install -y python3-pip python3-venv nginx certbot python3-certbot-nginx

# Install Node.js for Playwright
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

4. **Setup application**:
```bash
cd /home/ubuntu
git clone <your-repo-url> llm-quiz
cd llm-quiz
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
playwright install-deps
```

5. **Configure environment**:
```bash
cp .env.example .env
nano .env  # Edit with your credentials
```

6. **Create systemd service** (`/etc/systemd/system/quiz-solver.service`):
```ini
[Unit]
Description=LLM Analysis Quiz Solver
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/llm-quiz
Environment="PATH=/home/ubuntu/llm-quiz/venv/bin"
ExecStart=/home/ubuntu/llm-quiz/venv/bin/uvicorn app:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

7. **Enable and start service**:
```bash
sudo systemctl daemon-reload
sudo systemctl enable quiz-solver
sudo systemctl start quiz-solver
sudo systemctl status quiz-solver
```

8. **Configure nginx** (`/etc/nginx/sites-available/quiz-solver`):
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

9. **Enable site and setup HTTPS**:
```bash
sudo ln -s /etc/nginx/sites-available/quiz-solver /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
sudo certbot --nginx -d your-domain.com
```

10. **Your endpoint**: `https://your-domain.com/`

## Option 3: Google Cloud Run

1. **Create Dockerfile**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium
RUN playwright install-deps chromium

COPY . .

ENV PORT=8080
ENV HEADLESS=true

CMD uvicorn app:app --host 0.0.0.0 --port $PORT
```

2. **Build and push**:
```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/quiz-solver
```

3. **Deploy**:
```bash
gcloud run deploy quiz-solver \
  --image gcr.io/YOUR_PROJECT_ID/quiz-solver \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars STUDENT_EMAIL=your-email@example.com \
  --set-env-vars STUDENT_SECRET=your-secret \
  --set-env-vars ANTHROPIC_API_KEY=your-api-key \
  --set-env-vars DEFAULT_LLM_PROVIDER=anthropic \
  --memory 2Gi \
  --timeout 300
```

4. **Your endpoint**: Provided by Cloud Run (e.g., `https://quiz-solver-xxx-uc.a.run.app/`)

## Option 4: DigitalOcean App Platform

1. **Create app.yaml**:
```yaml
name: quiz-solver
services:
- name: web
  github:
    repo: your-username/llm-analysis-quiz
    branch: main
  run_command: uvicorn app:app --host 0.0.0.0 --port 8080
  environment_slug: python
  envs:
  - key: STUDENT_EMAIL
    value: ${STUDENT_EMAIL}
  - key: STUDENT_SECRET
    value: ${STUDENT_SECRET}
  - key: ANTHROPIC_API_KEY
    value: ${ANTHROPIC_API_KEY}
  - key: DEFAULT_LLM_PROVIDER
    value: anthropic
  instance_size_slug: basic-s
  instance_count: 1
```

2. **Deploy via CLI or Web UI**

3. **Your endpoint**: Provided by App Platform

## Environment Variables Checklist

For all deployment options, ensure these are set:

- ✅ `STUDENT_EMAIL` - Your email from Google Form
- ✅ `STUDENT_SECRET` - Your secret from Google Form
- ✅ `ANTHROPIC_API_KEY` - If using Anthropic
- ✅ `OPENAI_API_KEY` - If using OpenAI
- ✅ `DEFAULT_LLM_PROVIDER` - `anthropic` or `openai`
- ✅ `HEADLESS` - `true` for production
- ✅ `QUIZ_TIMEOUT` - `170` (seconds)

## Testing Your Deployment

1. **Health check**:
```bash
curl https://your-endpoint.com/health
```

2. **Invalid secret (should return 403)**:
```bash
curl -X POST https://your-endpoint.com/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","secret":"wrong","url":"http://example.com"}'
```

3. **Demo quiz**:
```bash
curl -X POST https://your-endpoint.com/ \
  -H "Content-Type: application/json" \
  -d '{
    "email":"your-email@example.com",
    "secret":"your-secret",
    "url":"https://tds-llm-analysis.s-anand.net/demo"
  }'
```

## Monitoring

### View logs:

**Heroku**:
```bash
heroku logs --tail
```

**AWS EC2**:
```bash
sudo journalctl -u quiz-solver -f
```

**Google Cloud Run**:
```bash
gcloud run services logs read quiz-solver --limit 50
```

### Key metrics to monitor:
- Response time (should be < 3 minutes)
- Success rate
- LLM API usage
- Memory usage
- Error rates

## Troubleshooting

### Playwright issues:
```bash
# Reinstall browsers
playwright install chromium
playwright install-deps chromium
```

### Memory issues:
- Increase instance size
- Monitor browser cleanup
- Check for memory leaks

### Timeout issues:
- Verify network connectivity
- Check LLM API response times
- Increase `QUIZ_TIMEOUT` if needed

## Security Best Practices

1. **Never commit secrets** - Use environment variables
2. **Use HTTPS** - Always in production
3. **Validate inputs** - Check email and secret format
4. **Rate limiting** - Prevent abuse
5. **Monitor logs** - Watch for suspicious activity
6. **Update dependencies** - Keep packages current

## Cost Estimation

### AWS EC2 (t2.medium):
- Instance: ~$30/month
- Domain: ~$12/year
- Total: ~$30-40/month

### Heroku:
- Hobby dyno: $7/month
- With Playwright: May need Performance ($25/month)

### Google Cloud Run:
- Pay per request
- Estimated: $5-20/month for moderate usage

### LLM API Costs:
- Anthropic Claude: ~$0.003/request
- OpenAI GPT-4: ~$0.01-0.03/request
- Budget for testing: $10-50/month

## Support

If deployment issues arise:
1. Check logs for errors
2. Verify environment variables
3. Test locally first
4. Review the troubleshooting section
5. Open a GitHub issue with details
