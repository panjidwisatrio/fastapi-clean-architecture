# Cloud Platform Deployment

Deploy FastAPI Clean Architecture to major cloud providers.

## AWS (Amazon Web Services)

### EC2 Deployment

1. Launch EC2 instance (Ubuntu 22.04)
2. Install dependencies
3. Follow [Production Deployment](production.md) guide

### Elastic Beanstalk

```bash
# Install EB CLI
pip install awsebcli

# Initialize
eb init -p python-3.11 fastapi-app

# Create environment
eb create fastapi-prod

# Deploy
eb deploy
```

### ECS (Elastic Container Service)

Use Docker image from [Docker Deployment](docker.md).

### Lambda + API Gateway

For serverless deployment:

```python
# handler.py
from mangum import Mangum
from app.main import app

handler = Mangum(app)
```

## Azure

### App Service

```bash
# Install Azure CLI
az login

# Create resource group
az group create --name fastapi-rg --location eastus

# Create App Service plan
az appservice plan create \
  --name fastapi-plan \
  --resource-group fastapi-rg \
  --sku B1 \
  --is-linux

# Deploy
az webapp up \
  --name fastapi-app \
  --resource-group fastapi-rg \
  --runtime "PYTHON:3.11"
```

### Container Instances

```bash
# Build and push to Azure Container Registry
az acr create --name fastapiregistry --resource-group fastapi-rg --sku Basic
docker build -t fastapiregistry.azurecr.io/fastapi-app:latest .
docker push fastapiregistry.azurecr.io/fastapi-app:latest

# Deploy container
az container create \
  --name fastapi-container \
  --resource-group fastapi-rg \
  --image fastapiregistry.azurecr.io/fastapi-app:latest \
  --ports 8000
```

## Google Cloud Platform (GCP)

### Cloud Run

```bash
# Install gcloud CLI
gcloud auth login

# Build and deploy
gcloud run deploy fastapi-app \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Compute Engine

1. Create VM instance
2. Follow [Production Deployment](production.md) guide

### Kubernetes Engine (GKE)

```bash
# Create cluster
gcloud container clusters create fastapi-cluster \
  --num-nodes=2

# Deploy
kubectl apply -f kubernetes/
```

## Heroku

```bash
# Install Heroku CLI
heroku login

# Create app
heroku create fastapi-app

# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Deploy
git push heroku main

# Run migrations
heroku run alembic upgrade head
```

Create `Procfile`:

```
web: gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```

## DigitalOcean

### App Platform

1. Connect GitHub repository
2. Configure build settings
3. Add database
4. Deploy

### Droplet

1. Create Droplet (Ubuntu)
2. Follow [Production Deployment](production.md) guide

## Railway

Simple deployment:

1. Connect GitHub repository
2. Add PostgreSQL database
3. Set environment variables
4. Deploy automatically

## Render

1. Create Web Service
2. Connect repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add PostgreSQL database

## Environment Variables

All platforms require these variables:

```env
DATABASE_URL=postgresql://...
SECRET_KEY=your-secret-key
ENVIRONMENT=production
ALLOWED_ORIGINS=https://your-domain.com
```

## Cost Considerations

| Platform | Free Tier | Entry Cost | Best For |
|----------|-----------|------------|----------|
| Heroku | Yes (limited) | $7/month | Small apps |
| Railway | $5 credit | $5/month | Startups |
| Render | Yes | $7/month | Simple deploys |
| DigitalOcean | No | $5/month | Control |
| AWS | Free tier 1yr | Varies | Scalability |
| GCP | $300 credit | Varies | Enterprise |
| Azure | $200 credit | Varies | Microsoft stack |

## Next Steps

- [Production Deployment](production.md)
- [Docker Deployment](docker.md)
- [CI/CD Pipeline](cicd.md)
