#!/bin/bash
# Web Deployment Guide for Witch's Weapon

# This script contains instructions for deploying to various platforms

## LOCAL DEVELOPMENT

# 1. Install dependencies
pip install -r requirements.txt

# 2. Run development server
python web_app.py

# Browser: http://localhost:5000


## DOCKER DEPLOYMENT (Local)

# 1. Build Docker image
docker build -t witchweapon:web .

# 2. Run container
docker run -p 8000:8000 witchweapon:web

# Browser: http://localhost:8000


## DOCKER COMPOSE (Local with hot-reload)

# 1. Start service
docker-compose up

# Browser: http://localhost:8000

# 2. Hot-reload during development
# Just edit files and they'll reload automatically


## HEROKU DEPLOYMENT

# 1. Create Heroku app
heroku apps:create witchweapon-web

# 2. Set environment variables (if needed)
heroku config:set FLASK_ENV=production

# 3. Deploy using git
git push heroku main:main

# 4. View logs
heroku logs --tail

# 5. Open in browser
heroku open


## AWS DEPLOYMENT (Elastic Beanstalk)

# 1. Install EB CLI
curl https://bootstrap.pypa.io/elbv2.py | python

# 2. Initialize application
eb init -p "python-3.12" witchweapon-web

# 3. Create environment
eb create witchweapon-web-env

# 4. Deploy
eb deploy

# 5. Open application
eb open


## GOOGLE CLOUD RUN

# 1. Build and push image
gcloud builds submit --tag gcr.io/PROJECT_ID/witchweapon-web .

# 2. Deploy to Cloud Run
gcloud run deploy witchweapon-web \
  --image gcr.io/PROJECT_ID/witchweapon-web \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --timeout 120

# 3. Get service URL
gcloud run services describe witchweapon-web --platform managed --region us-central1


## AZURE CONTAINER INSTANCES

# 1. Build and push image
az acr build --registry myregistry --image witchweapon-web:latest .

# 2. Deploy container
az container create \
  --resource-group myresourcegroup \
  --name witchweapon-web \
  --image myregistry.azurecr.io/witchweapon-web:latest \
  --ports 8000 \
  --cpu 1 --memory 1 \
  --registry-login-server myregistry.azurecr.io \
  --registry-username <username> \
  --registry-password <password>


## KUBERNETES DEPLOYMENT

# 1. Create deployment YAML
kubectl create deployment witchweapon-web --image=witchweapon:web

# 2. Expose service
kubectl expose deployment witchweapon-web --type=LoadBalancer --port=8000

# 3. Check deployment
kubectl get deployments
kubectl get services


## DIGITALOCEAN APP PLATFORM

# 1. Push Docker image
docker tag witchweapon:web registry.digitalocean.com/myregistry/witchweapon:web
docker push registry.digitalocean.com/myregistry/witchweapon:web

# 2. Create app.yaml and deploy via web console or CLI
doctl apps create --spec app.yaml


## ENVIRONMENT VARIABLES

# Optional environment variables for web_app.py:
export FLASK_ENV=production
export FLASK_DEBUG=0
export SECRET_KEY=your-secure-key
export PORT=8000

# For production, use a strong SECRET_KEY


## PRODUCTION CHECKLIST

[] requirements.txt updated with all dependencies
[] Dockerfile builds without errors
[] docker-compose.yml tested locally
[] Environment variables configured
[] FLASK_DEBUG=0 in production
[] Static files served correctly
[] Error logging configured
[] Health check endpoint working
[] Load balancer configured (if needed)
[] SSL/TLS certificate installed
[] Domain name configured
[] Backup strategy in place


## PERFORMANCE OPTIMIZATION

# 1. Use gunicorn with multiple workers
gunicorn --workers 4 --bind 0.0.0.0:8000 web_app:app

# 2. Enable caching headers in production
# Add to web_app.py:
# @app.after_request
# def add_cache_headers(response):
#     response.headers['Cache-Control'] = 'public, max-age=3600'
#     return response

# 3. Use CDN for assets
# Upload static files to S3/CloudFlare/etc.

# 4. Enable compression
# Add to web_app.py:
# from flask_compress import Compress
# Compress(app)


## MONITORING & LOGGING

# 1. Set up application monitoring
# - Application Performance Monitoring (APM)
# - Error tracking (Sentry)
# - Log aggregation (ELK Stack, CloudWatch)

# 2. Health check endpoint
curl http://localhost:8000/health

# 3. Metrics endpoint
curl http://localhost:8000/metrics


## TROUBLESHOOTING

# Port already in use
lsof -i :8000
kill -9 <PID>

# Docker build fails
docker build --no-cache -t witchweapon:web .

# Container won't start
docker logs <container_id>

# Permission denied
chmod +x deploy-guide.sh

# Module import errors
pip install --upgrade -r requirements.txt

# Clear Python cache
find . -type d -name __pycache__ -exec rm -r {} +
find . -type f -name '*.pyc' -delete
