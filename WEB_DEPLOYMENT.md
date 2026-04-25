# 🧙‍♀️ Witch's Weapon - Web Edition Deployment Guide

Welcome to the Witch's Weapon Web Edition! This guide covers everything you need to deploy the game to the web.

## Quick Start (Local Development)

### 1. **Simple Start**
```bash
bash start-web.sh
```
Visit: **http://localhost:5000**

### 2. **Manual Start**
```bash
# Install dependencies
pip install -r requirements.txt

# Run web server
python web_app.py
```

### 3. **Docker (Optional)**
```bash
# Build image
docker build -t witchweapon:web .

# Run container
docker run -p 8000:8000 witchweapon:web
```

---

## Deployment Options

Choose one of these deployment targets:

### 🚀 **Heroku** (Recommended for beginners)
```bash
# 1. Create app
heroku apps:create witchweapon-web

# 2. Deploy
git push heroku main

# 3. Open
heroku open
```
**Pros:** Free tier, simple setup, auto-SSL
**Cons:** Limited performance

### 🌩️ **AWS Elastic Beanstalk**
```bash
eb init -p python-3.12 witchweapon-web
eb create witchweapon-env
eb deploy
```
**Pros:** Scalable, production-grade
**Cons:** More complex setup

### ☁️ **Google Cloud Run**
```bash
gcloud run deploy witchweapon-web \
  --source . \
  --platform managed \
  --region us-central1
```
**Pros:** Serverless, pay-per-request
**Cons:** Cold starts

### 🔷 **Azure Container Instances**
```bash
az container create \
  --resource-group mygroup \
  --name witchweapon-web \
  --image witchweapon:web
```
**Pros:** Enterprise-grade
**Cons:** Learning curve

### 🌊 **DigitalOcean App Platform**
```bash
doctl apps create --spec app.yaml
```
**Pros:** Affordable, simple
**Cons:** Less feature-rich

---

## Features

### ✨ **Fully Integrated**
- ✅ Daily Missions system
- ✅ Cross-platform portability (web, mobile, PC, console)
- ✅ Performance tier scaling
- ✅ Responsive UI
- ✅ Input assistance modes

### 🔌 **API Endpoints**
All available via REST API:

```bash
# Health check
curl http://localhost:5000/health

# Game status
curl http://localhost:5000/api/status

# Get output
curl http://localhost:5000/api/output

# Send input
curl -X POST http://localhost:5000/api/input \
  -H "Content-Type: application/json" \
  -d '{"input": "1"}'
```

### 🎮 **Game Features**
- Combat system with enemies
- Weapon upgrades and progression
- Daily missions with rewards
- PvP matchmaking
- Visual novel sequences
- Cross-platform save data

---

## Configuration

### Environment Variables
Create a `.env` file (copy from `.env.example`):

```bash
FLASK_ENV=production
SECRET_KEY=your-secure-key
PORT=8000
```

### Performance Tuning
Edit `web_app.py` for production:
```python
# Increase number of workers
gunicorn --workers 4 --timeout 120 web_app:app
```

---

## Deployment Checklist

- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file configured with `SECRET_KEY`
- [ ] Docker image builds (`docker build -t witchweapon:web .`)
- [ ] Local testing passes (`bash test-deployment.sh`)
- [ ] Health check responds (http://localhost:5000/health)
- [ ] API endpoints work (`/api/status`, `/api/output`)
- [ ] Git committed (`git add . && git commit`)
- [ ] Cloud provider account ready
- [ ] Domain name configured (optional)
- [ ] SSL/TLS certificate enabled

---

## Architecture

```
┌─────────────────────────────────────────┐
│         Web Browser (Client)            │
└────────────┬────────────────────────────┘
             │ HTTP/WebSocket
┌────────────▼────────────────────────────┐
│   Flask Web Server (web_app.py)         │
│  ├─ GET / (Main game terminal UI)       │
│  ├─ POST / (Input handling)             │
│  ├─ GET /health (Health check)          │
│  ├─ GET /api/status (Game status)       │
│  ├─ GET /api/output (Game output)       │
│  └─ POST /api/input (REST API input)    │
└────────────┬────────────────────────────┘
             │ Python imports
┌────────────▼────────────────────────────┐
│    Portability Framework (Core)         │
│  ├─ Layer 1: Game Logic                 │
│  ├─ Layer 2: Simulation Rules           │
│  ├─ Layer 3: Presentation               │
│  ├─ Layer 4: Input System               │
│  └─ Layer 5: Platform Services          │
└─────────────────────────────────────────┘
```

---

## Monitoring & Logging

### Local Development
```bash
# Enable verbose logging
export FLASK_DEBUG=1
python web_app.py
```

### Production
```bash
# Check logs
docker logs <container-id>

# Or via cloud provider
heroku logs --tail
gcloud run logs read
```

---

## Performance Metrics

| Platform | Startup | Response | Scalability |
|----------|---------|----------|-------------|
| Local | <100ms | <50ms | Single thread |
| Heroku | 1-3s | 100-200ms | Auto scaling |
| Cloud Run | 2-5s | 50-100ms | Serverless |
| EC2/GKE | <500ms | 50-100ms | Auto scaling |

---

## Security Best Practices

- ✅ Use strong `SECRET_KEY` in production
- ✅ Set `FLASK_DEBUG=0` in production
- ✅ Use HTTPS/SSL in production
- ✅ Enable CORS only for trusted domains
- ✅ Validate all user inputs
- ✅ Use environment variables for secrets
- ✅ Keep dependencies updated
- ✅ Monitor for suspicious activity

---

## Troubleshooting

### Port Already in Use
```bash
lsof -i :5000
kill -9 <PID>
```

### Module Import Errors
```bash
pip install --upgrade -r requirements.txt
python -m pip install --force-reinstall -r requirements.txt
```

### Docker Build Fails
```bash
docker build --no-cache -t witchweapon:web .
```

### Timeout Issues
Increase timeout in `web_app.py`:
```python
queue.get(timeout=600)  # Increase from 300
```

---

## Support & Resources

- 📖 **Full Deployment Guide**: See `DEPLOYMENT_GUIDE.md`
- 🐛 **Issues**: Check GitHub issues
- 💬 **Discussions**: Community forums
- 📚 **Documentation**: `/docs` folder

---

## License

See LICENSE file for details.

---

## Getting Help

If deployment issues occur:

1. ✅ Run the test script: `bash test-deployment.sh`
2. 📋 Check logs: `Flask debug=True` or cloud logs
3. 🔧 Review configuration in `.env` file
4. 📞 Open an issue with error details

---

**Happy deploying! 🚀**
