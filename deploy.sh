#!/bin/bash

echo "🚀 DocChat RAG Deployment Helper"
echo "================================"
echo ""
echo "Select deployment platform:"
echo "1) Railway (Recommended - Easy)"
echo "2) Fly.io (Docker-based)"
echo "3) Render (Full-stack)"
echo "4) Google Cloud Run"
echo "5) Docker Compose (VPS)"
echo ""
read -p "Enter choice [1-5]: " choice

case $choice in
    1)
        echo "📦 Deploying to Railway..."
        echo ""
        echo "Steps:"
        echo "1. Install Railway CLI: npm install -g @railway/cli"
        echo "2. Run: railway login"
        echo "3. Run: railway init"
        echo "4. Run: railway up"
        echo "5. Add OPENAI_API_KEY in Railway dashboard"
        echo ""
        echo "Creating railway.json config..."
        cat > railway.json << EOF
{
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "backend/Dockerfile"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port \$PORT",
    "healthcheckPath": "/health",
    "restartPolicyType": "ON_FAILURE"
  }
}
EOF
        echo "✅ railway.json created"
        ;;
        
    2)
        echo "🐳 Deploying to Fly.io..."
        echo ""
        echo "Creating fly.toml..."
        cat > fly.toml << EOF
app = "docchat-rag"
primary_region = "ord"

[build]
  dockerfile = "backend/Dockerfile"

[env]
  PORT = "8080"

[http_service]
  internal_port = 8080
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true

[[services]]
  protocol = "tcp"
  internal_port = 8080
  ports = [
    { port = 80, handlers = ["http"] },
    { port = 443, handlers = ["tls", "http"] }
  ]
EOF
        echo "✅ fly.toml created"
        echo ""
        echo "Next steps:"
        echo "1. Install Fly CLI: curl -L https://fly.io/install.sh | sh"
        echo "2. Run: fly launch"
        echo "3. Run: fly secrets set OPENAI_API_KEY=your-key"
        echo "4. Run: fly deploy"
        ;;
        
    3)
        echo "🔷 Deploying to Render..."
        echo ""
        echo "Creating render.yaml..."
        cat > render.yaml << EOF
services:
  - type: web
    name: docchat-backend
    runtime: python
    repo: https://github.com/YOUR_GITHUB/docchat-rag
    buildCommand: cd backend && pip install -r requirements.txt
    startCommand: cd backend && uvicorn app.main:app --host 0.0.0.0 --port \$PORT
    envVars:
      - key: OPENAI_API_KEY
        sync: false
      - key: PYTHON_VERSION
        value: 3.11.0
        
  - type: web
    name: docchat-frontend  
    runtime: static
    repo: https://github.com/YOUR_GITHUB/docchat-rag
    buildCommand: cd frontend && npm install && npm run build
    staticPublishPath: ./frontend/dist
    envVars:
      - key: BACKEND_URL
        value: https://docchat-backend.onrender.com
EOF
        echo "✅ render.yaml created"
        echo ""
        echo "Next steps:"
        echo "1. Push to GitHub"
        echo "2. Connect GitHub repo in Render dashboard"
        echo "3. Add OPENAI_API_KEY in environment settings"
        ;;
        
    4)
        echo "☁️ Deploying to Google Cloud Run..."
        echo ""
        echo "Creating cloudbuild.yaml..."
        cat > cloudbuild.yaml << EOF
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/\$PROJECT_ID/docchat-backend', '-f', 'backend/Dockerfile', '.']
  
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/\$PROJECT_ID/docchat-backend']
    
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'docchat-backend'
      - '--image=gcr.io/\$PROJECT_ID/docchat-backend'
      - '--region=us-central1'
      - '--platform=managed'
      - '--allow-unauthenticated'
      - '--set-env-vars=OPENAI_API_KEY=\${_OPENAI_API_KEY}'

substitutions:
  _OPENAI_API_KEY: 'your-key-here'
EOF
        echo "✅ cloudbuild.yaml created"
        echo ""
        echo "Next steps:"
        echo "1. Install gcloud CLI"
        echo "2. Run: gcloud builds submit"
        echo "3. Access at: https://docchat-backend-xxxxx.run.app"
        ;;
        
    5)
        echo "🖥️ Deploying with Docker Compose (VPS)..."
        echo ""
        echo "Creating production docker-compose.yml..."
        cat > docker-compose.prod.yml << EOF
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "80:8000"
    environment:
      - OPENAI_API_KEY=\${OPENAI_API_KEY}
    volumes:
      - ./data:/app/data
    restart: always
    
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    ports:
      - "3000:80"
    depends_on:
      - backend
    restart: always

volumes:
  data:
EOF
        echo "✅ docker-compose.prod.yml created"
        echo ""
        echo "Next steps:"
        echo "1. Copy to VPS: scp -r . user@your-vps:/opt/docchat"
        echo "2. SSH to VPS: ssh user@your-vps"
        echo "3. Run: docker-compose -f docker-compose.prod.yml up -d"
        echo "4. Setup Nginx reverse proxy for HTTPS"
        ;;
esac

echo ""
echo "📚 Additional Resources:"
echo "- Set up GitHub Actions for CI/CD"
echo "- Configure monitoring (Sentry, LogRocket)"
echo "- Add rate limiting and authentication"
echo "- Consider CDN for frontend assets"
echo ""
echo "Need help? Check deployment docs in README.md"