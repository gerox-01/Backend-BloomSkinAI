# CI/CD Setup Guide - GitHub Actions → Cloud Run

This guide will help you set up automatic deployments to Google Cloud Run whenever you push code to GitHub.

---

## Overview

Once set up, your workflow will:
1. ✅ Automatically deploy when you push to `develop` or `main` branch
2. ✅ Build and deploy in ~2-3 minutes
3. ✅ Zero downtime deployments
4. ✅ Show deployment URL in GitHub Actions logs

---

## Step 1: Create a Service Account for GitHub Actions

```bash
# Set your project
export PROJECT_ID=bloomskinai-412aa

# Create service account
gcloud iam service-accounts create github-actions \
  --display-name="GitHub Actions Deployment Account" \
  --project=$PROJECT_ID

# Get the service account email
export SA_EMAIL=github-actions@${PROJECT_ID}.iam.gserviceaccount.com

# Grant necessary roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/cloudbuild.builds.builder"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/iam.serviceAccountUser"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/firebase.admin"
```

---

## Step 2: Create Service Account Key

```bash
# Create and download the key
gcloud iam service-accounts keys create github-actions-key.json \
  --iam-account=$SA_EMAIL

# Display the key content (you'll need this for GitHub)
cat github-actions-key.json
```

**IMPORTANT:**
- Copy the entire JSON content
- Delete the file after copying: `rm github-actions-key.json`
- Never commit this file to git!

---

## Step 3: Add Secrets to GitHub

Go to your GitHub repository:

**URL:** `https://github.com/YOUR_USERNAME/YOUR_REPO/settings/secrets/actions`

Add these secrets (click "New repository secret"):

### Required Secrets:

1. **GCP_SA_KEY**
   - Value: Paste the entire JSON content from `github-actions-key.json`

2. **SECRET_KEY**
   - Value: `TByI7Rzw0bwZUGx-nz-jm7A_1PAwiI8U-TlWHdpGVsM`
   - (Or generate a new one: `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`)

3. **BACKEND_CORS_ORIGINS**
   - Value: `["https://your-frontend-url.com","http://localhost:3000"]`
   - Update with your actual frontend URL

4. **HAUT_AI_USERNAME**
   - Value: `gedaquito@gmail.com`

5. **HAUT_AI_PASSWORD**
   - Value: `BloomSkin02+*`

---

## Step 4: Push to GitHub

Once secrets are configured, simply push your code:

```bash
# Make sure you're on develop or main branch
git status

# Add all changes
git add .

# Commit
git commit -m "Add CI/CD with GitHub Actions"

# Push to trigger deployment
git push origin develop
```

---

## Step 5: Monitor Deployment

1. Go to GitHub Actions tab: `https://github.com/YOUR_USERNAME/YOUR_REPO/actions`
2. You'll see your deployment running
3. Click on it to see real-time logs
4. Deployment takes ~2-3 minutes

---

## How It Works

### Automatic Deployment Triggers:

- ✅ Push to `develop` branch → Auto-deploy
- ✅ Push to `main` branch → Auto-deploy
- ✅ Manual trigger → Go to Actions tab → "Run workflow"

### What Happens During Deployment:

1. GitHub Actions checks out your code
2. Authenticates with Google Cloud
3. Creates `.env.yaml` from GitHub secrets
4. Builds Docker container
5. Deploys to Cloud Run
6. Shows deployment URL

---

## Workflow File Location

The workflow is defined in:
```
.github/workflows/deploy-cloud-run.yml
```

You can customize:
- Branch names
- Memory/CPU settings
- Environment variables
- Deployment region

---

## Testing the Setup

### First Time Setup:

```bash
# 1. Initialize git (if not already)
git init

# 2. Add GitHub remote
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# 3. Create develop branch
git checkout -b develop

# 4. Add and commit all files
git add .
git commit -m "Initial commit with CI/CD"

# 5. Push to GitHub
git push -u origin develop
```

### After Setup - Daily Workflow:

```bash
# Make your changes
# Edit some files...

# Commit and push
git add .
git commit -m "Your change description"
git push

# 🎉 Automatic deployment starts!
```

---

## Advanced: Environment-Specific Deployments

You can modify the workflow to deploy to different environments:

### Staging + Production:

```yaml
# Deploy to staging on develop branch
- name: Deploy to Staging
  if: github.ref == 'refs/heads/develop'
  run: |
    gcloud run deploy bloomskinai-staging \
      --source . \
      --region us-central1

# Deploy to production on main branch
- name: Deploy to Production
  if: github.ref == 'refs/heads/main'
  run: |
    gcloud run deploy bloomskinai-412aa \
      --source . \
      --region us-central1
```

---

## Monitoring Deployments

### View Logs:
```bash
# GitHub Actions logs
https://github.com/YOUR_USERNAME/YOUR_REPO/actions

# Cloud Run logs
gcloud run services logs tail bloomskinai-412aa --region us-central1
```

### Check Deployment Status:
```bash
gcloud run services describe bloomskinai-412aa --region us-central1
```

---

## Troubleshooting

### Issue: "Permission denied" in GitHub Actions

**Solution:** Check that the service account has all required roles (Step 1)

### Issue: "Invalid credentials"

**Solution:**
1. Make sure `GCP_SA_KEY` secret contains valid JSON
2. Regenerate the service account key if needed

### Issue: Deployment fails on push

**Solution:**
1. Check GitHub Actions logs for specific error
2. Verify all secrets are set correctly
3. Ensure service account has Firebase Admin role

---

## Security Best Practices

1. ✅ Never commit `.env.yaml` to git (already in .gitignore)
2. ✅ Never commit service account keys
3. ✅ Use GitHub Secrets for all sensitive data
4. ✅ Rotate secrets periodically
5. ✅ Use different service accounts for staging/production
6. ✅ Review GitHub Actions logs for sensitive data before sharing

---

## Cost Considerations

- **GitHub Actions:** 2,000 free minutes/month
- **Cloud Build:** 120 build-minutes/day free
- **Cloud Run:** Same pricing as before ($0-5/month for small apps)

**Typical deployment:**
- Build time: ~2 minutes
- You can do ~60 deployments per month for free

---

## Next Steps

1. ✅ Set up secrets in GitHub
2. ✅ Push code to trigger first deployment
3. ✅ Add status badge to README (optional)
4. ✅ Set up Slack/Discord notifications (optional)
5. ✅ Add automated tests before deployment (optional)

---

## Status Badge (Optional)

Add this to your README.md to show deployment status:

```markdown
![Deploy to Cloud Run](https://github.com/YOUR_USERNAME/YOUR_REPO/workflows/Deploy%20to%20Cloud%20Run/badge.svg)
```

---

## Support

- GitHub Actions Docs: https://docs.github.com/en/actions
- Cloud Run Docs: https://cloud.google.com/run/docs/continuous-deployment-with-cloud-build
- Issues: Check GitHub Actions logs and Cloud Run logs

---

**You're all set! 🚀**

Every push to `develop` or `main` will now automatically deploy your backend to Cloud Run!
