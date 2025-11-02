# Google Cloud Run Deployment Guide

Complete step-by-step guide to deploy your BloomSkin FastAPI backend to Google Cloud Run.

---

## Prerequisites

1. Google Cloud account (get $300 free credit for new users)
2. Your Firebase project already created
3. Docker installed on your computer (for local testing)

---

## Step 1: Install Google Cloud CLI

### macOS
```bash
brew install --cask google-cloud-sdk
```

### Windows
Download from: https://cloud.google.com/sdk/docs/install

### Linux
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

---

## Step 2: Initialize Google Cloud

```bash
# Login to your Google account
gcloud auth login

# Set your project (use the same project as your Firebase)
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

**To find your PROJECT_ID:**
- Go to Firebase Console: https://console.firebase.google.com/
- Your project ID is shown under Project Settings

---

## Step 3: Prepare Environment Variables

Create a file called `.env.yaml` in your project root (DO NOT commit this file):

```yaml
# .env.yaml
APP_NAME: "BloomSkin API"
APP_VERSION: "1.0.0"
APP_ENV: "production"
DEBUG: "false"

# API Settings
API_V1_PREFIX: "/api/v1"
HOST: "0.0.0.0"
PORT: "8080"
LOG_LEVEL: "INFO"

# CORS - Add your frontend URLs here
BACKEND_CORS_ORIGINS: '["https://your-frontend-url.com", "https://www.your-frontend-url.com"]'

# Firebase - These will come from your Firebase project
FIREBASE_PROJECT_ID: "your-firebase-project-id"
FIREBASE_STORAGE_BUCKET: "your-project-id.appspot.com"

# Rate Limiting
RATE_LIMIT_ENABLED: "true"
RATE_LIMIT_PER_MINUTE: "60"

# Haut.ai Integration (if applicable)
HAUTAI_API_KEY: "your-hautai-api-key"
HAUTAI_COMPANY_ID: "your-company-id"
HAUTAI_BATCH_ID: "your-batch-id"
```

**Important:** Replace all placeholder values with your actual values.

---

## Step 4: Set Up Firebase Credentials

Your app uses Firebase, so you need to provide credentials to Cloud Run:

### Option A: Using Application Default Credentials (Recommended)

```bash
# This allows Cloud Run to automatically access Firebase in the same project
gcloud run services add-iam-policy-binding bloomskin-api \
  --region=us-central1 \
  --member="serviceAccount:YOUR_PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/firebase.admin"
```

### Option B: Using Service Account Key (if needed)

1. Go to: https://console.firebase.google.com/project/YOUR_PROJECT/settings/serviceaccounts/adminsdk
2. Click "Generate new private key"
3. Save the JSON file securely
4. Add to `.env.yaml`:
   ```yaml
   GOOGLE_APPLICATION_CREDENTIALS: "/app/firebase-credentials.json"
   ```

---

## Step 5: Test Docker Build Locally (Optional but Recommended)

```bash
# Build the Docker image
docker build -t bloomskin-api .

# Run locally to test
docker run -p 8080:8080 --env-file .env bloomskin-api

# Test in browser
open http://localhost:8080/health
```

---

## Step 6: Deploy to Google Cloud Run

### First Deployment

```bash
# Deploy the service
gcloud run deploy bloomskin-api \
  --source . \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --env-vars-file .env.yaml \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --timeout 300
```

**Command explanation:**
- `bloomskin-api`: Your service name
- `--source .`: Build from current directory
- `--region us-central1`: Deployment region (change if needed)
- `--allow-unauthenticated`: Public API (change if you need auth)
- `--env-vars-file .env.yaml`: Load environment variables
- `--memory 512Mi`: RAM allocation (can increase if needed)
- `--min-instances 0`: Scales to zero when not used (free tier friendly)
- `--max-instances 10`: Maximum concurrent instances
- `--timeout 300`: 5 minute timeout for requests

### Available Regions
- `us-central1` (Iowa) - Good for North America
- `us-east1` (South Carolina)
- `europe-west1` (Belgium) - Good for Europe
- `asia-northeast1` (Tokyo) - Good for Asia

---

## Step 7: After Deployment

After successful deployment, you'll see:

```
Service [bloomskin-api] revision [bloomskin-api-00001-abc] has been deployed and is serving 100 percent of traffic.
Service URL: https://bloomskin-api-xxxxx-uc.a.run.app
```

**Test your deployment:**
```bash
# Health check
curl https://your-service-url.run.app/health

# API docs
open https://your-service-url.run.app/docs
```

---

## Step 8: Set Up Custom Domain (Optional)

If you want to use your own domain like `api.bloomskin.com`:

```bash
# Map your domain
gcloud run domain-mappings create \
  --service bloomskin-api \
  --domain api.bloomskin.com \
  --region us-central1
```

Then add the DNS records shown by Google to your domain registrar.

---

## Updating Your Deployment

When you make changes to your code:

```bash
# Simply redeploy
gcloud run deploy bloomskin-api \
  --source . \
  --region us-central1
```

Cloud Run will automatically:
- Build a new container image
- Deploy with zero downtime
- Gradually shift traffic to the new version

---

## Monitoring and Logs

### View Logs
```bash
# Real-time logs
gcloud run services logs tail bloomskin-api --region us-central1

# Or via web console
open https://console.cloud.google.com/run
```

### Monitor Performance
Go to: https://console.cloud.google.com/run/detail/us-central1/bloomskin-api/metrics

---

## Cost Estimation

Google Cloud Run pricing (as of 2024):

**Free Tier (monthly):**
- 2 million requests
- 360,000 GB-seconds of memory
- 180,000 vCPU-seconds

**Your estimated cost:**
- With min-instances=0: $0-5/month for small apps
- With min-instances=1: ~$10-15/month (always warm, no cold starts)

**To keep costs low:**
- Use `--min-instances 0` for development
- Use `--min-instances 1` for production (eliminates cold starts)

---

## Troubleshooting

### Issue: "Permission denied"
```bash
# Grant yourself the necessary role
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="user:YOUR_EMAIL@gmail.com" \
  --role="roles/run.admin"
```

### Issue: "Build failed"
- Check your Dockerfile
- Make sure all dependencies are in requirements.txt
- Test build locally first

### Issue: "Service unhealthy"
- Check logs: `gcloud run services logs tail bloomskin-api`
- Verify environment variables are set correctly
- Test health endpoint: `/health`

### Issue: "Firebase connection failed"
- Make sure your Firebase project ID matches
- Verify service account has Firebase Admin permissions
- Check Firebase credentials are properly configured

---

## Security Best Practices

1. **Never commit `.env.yaml`** - Add to .gitignore
2. **Use Secret Manager for sensitive data:**
   ```bash
   gcloud secrets create hautai-api-key --data-file=-
   # Then reference in deployment
   ```
3. **Enable Cloud Armor** for DDoS protection
4. **Set up Cloud IAM** properly
5. **Use HTTPS only** (automatic with Cloud Run)

---

## Next Steps

1. Set up CI/CD with GitHub Actions
2. Configure monitoring and alerts
3. Set up Cloud CDN for static assets
4. Implement Cloud Armor for security
5. Set up automated backups

---

## Quick Reference Commands

```bash
# Deploy
gcloud run deploy bloomskin-api --source . --region us-central1

# View logs
gcloud run services logs tail bloomskin-api --region us-central1

# Update environment variables
gcloud run services update bloomskin-api \
  --env-vars-file .env.yaml \
  --region us-central1

# Delete service
gcloud run services delete bloomskin-api --region us-central1

# List all services
gcloud run services list
```

---

## Support Resources

- Google Cloud Run Docs: https://cloud.google.com/run/docs
- Pricing Calculator: https://cloud.google.com/products/calculator
- Community Support: https://stackoverflow.com/questions/tagged/google-cloud-run
- Your Firebase Console: https://console.firebase.google.com/

---

**You're ready to deploy! 🚀**

Start with Step 1 and work through each step. If you get stuck, check the troubleshooting section or the logs.
