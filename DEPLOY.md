# BriteCo Ad Generator - Google Cloud Run Deployment Guide

## Prerequisites
1. Google Cloud account with billing enabled
2. Google Cloud CLI installed: https://cloud.google.com/sdk/docs/install
3. Docker installed (optional, for local testing)

---

## Step 1: Initial Setup (One-time)

### 1.1 Install Google Cloud CLI
Download and install from: https://cloud.google.com/sdk/docs/install

### 1.2 Login to Google Cloud
```bash
gcloud auth login
```

### 1.3 Create a new project (or use existing)
```bash
gcloud projects create briteco-ad-generator --name="BriteCo Ad Generator"
gcloud config set project briteco-ad-generator
```

### 1.4 Enable required APIs
```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable iap.googleapis.com
```

---

## Step 2: Set Up API Keys as Secrets

Store your API keys securely in Google Secret Manager:

```bash
# Create secrets for each API key
echo -n "YOUR_ANTHROPIC_API_KEY" | gcloud secrets create ANTHROPIC_API_KEY --data-file=-
echo -n "YOUR_OPENAI_API_KEY" | gcloud secrets create OPENAI_API_KEY --data-file=-
echo -n "YOUR_GOOGLE_API_KEY" | gcloud secrets create GOOGLE_API_KEY --data-file=-
```

---

## Step 3: Deploy to Cloud Run

### 3.1 Navigate to your project folder
```bash
cd "C:\Users\DylanneCrugnale\Desktop\briteco-ad-generator-simple"
```

### 3.2 Deploy the application
```bash
gcloud run deploy briteco-ad-generator \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --timeout 300 \
  --set-secrets=ANTHROPIC_API_KEY=ANTHROPIC_API_KEY:latest,OPENAI_API_KEY=OPENAI_API_KEY:latest,GOOGLE_API_KEY=GOOGLE_API_KEY:latest
```

### 3.3 Get your app URL
After deployment, you'll see a URL like:
```
https://briteco-ad-generator-XXXXXX-uc.a.run.app
```

---

## Step 4: Set Up Google Authentication (IAP)

To restrict access to only your team members:

### 4.1 Go to Google Cloud Console
https://console.cloud.google.com/security/iap

### 4.2 Enable IAP for Cloud Run
1. Click on the "Cloud Run" tab
2. Find your service (briteco-ad-generator)
3. Toggle IAP to "ON"

### 4.3 Add team members
1. Click on the service name
2. Click "Add Principal"
3. Enter team member emails (e.g., sarah@briteco.com)
4. Select role: "IAP-secured Web App User"
5. Click "Save"

---

## Step 5: Custom Domain (Optional)

To use a custom domain like `ads.briteco.com`:

### 5.1 Verify domain ownership
```bash
gcloud domains verify briteco.com
```

### 5.2 Map custom domain
```bash
gcloud run domain-mappings create \
  --service briteco-ad-generator \
  --domain ads.briteco.com \
  --region us-central1
```

### 5.3 Update DNS
Add the DNS records shown in Cloud Console to your domain provider.

---

## Updating the App

To deploy updates after making changes:

```bash
cd "C:\Users\DylanneCrugnale\Desktop\briteco-ad-generator-simple"
gcloud run deploy briteco-ad-generator --source .
```

---

## Viewing Logs

To see application logs:
```bash
gcloud run logs read --service briteco-ad-generator --region us-central1
```

Or view in Cloud Console:
https://console.cloud.google.com/run/detail/us-central1/briteco-ad-generator/logs

---

## Cost Estimate

Cloud Run pricing (pay-per-use):
- CPU: $0.00002400 per vCPU-second
- Memory: $0.00000250 per GiB-second
- Requests: $0.40 per million requests

Estimated monthly cost for moderate team use: **$5-20/month**

Free tier includes:
- 2 million requests/month
- 360,000 GiB-seconds of memory
- 180,000 vCPU-seconds

---

## Troubleshooting

### "Permission denied" errors
Make sure you've granted the Cloud Build service account access to Secret Manager:
```bash
PROJECT_NUMBER=$(gcloud projects describe $(gcloud config get-value project) --format="value(projectNumber)")
gcloud secrets add-iam-policy-binding ANTHROPIC_API_KEY \
  --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### Build fails
Check the build logs:
```bash
gcloud builds list --limit=5
gcloud builds log BUILD_ID
```

### App not loading
Check the service logs:
```bash
gcloud run logs read --service briteco-ad-generator --limit=50
```
