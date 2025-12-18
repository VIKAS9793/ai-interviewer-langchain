# Deployment Guide

> Deploy AI Technical Interviewer to Google Cloud Run

---

## Prerequisites

1. [Google Cloud Account](https://cloud.google.com/) (Free tier available)
2. [gcloud CLI](https://cloud.google.com/sdk/docs/install) installed
3. [Gemini API Key](https://aistudio.google.com/app/apikey)

---

## Quick Deploy

### 1. Authenticate with GCP

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### 2. Store API Key in Secret Manager

```bash
echo -n "YOUR_GEMINI_API_KEY" | \
  gcloud secrets create google-api-key --data-file=-
```

### 3. Deploy to Cloud Run

```bash
gcloud run deploy ai-interviewer \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 256Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 1 \
  --set-secrets "GOOGLE_API_KEY=google-api-key:latest"
```

### 4. Access Your App

```
Service URL: https://ai-interviewer-xxxxx-uc.a.run.app
```

---

## Free Tier Limits

| Resource | Free Tier |
|----------|-----------|
| CPU | 180,000 vCPU-seconds/month |
| Memory | 360,000 GB-seconds/month |
| Requests | 2 million/month |
| Egress | 1 GB/month (North America) |

With `min-instances=0`, you only pay when the app is used.

---

## Configuration Options

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_API_KEY` | Gemini API key | Yes |
| `LOG_LEVEL` | Logging level (INFO, DEBUG) | No |

### Cloud Run Settings

```yaml
# Recommended for free tier
memory: 256Mi
cpu: 1
min-instances: 0
max-instances: 1
timeout: 300
```

---

## Monitoring

### View Logs

```bash
gcloud run logs read ai-interviewer --region us-central1
```

### Stream Logs

```bash
gcloud run logs tail ai-interviewer --region us-central1
```

---

## Updating

```bash
# Deploy new version
gcloud run deploy ai-interviewer --source .

# Rollback if needed
gcloud run services describe ai-interviewer --region us-central1
gcloud run services update-traffic ai-interviewer \
  --to-revisions PREVIOUS_REVISION=100
```

---

## Cleanup

```bash
# Delete service
gcloud run services delete ai-interviewer --region us-central1

# Delete secret
gcloud secrets delete google-api-key
```

---

## See Also

- [Setup Guide](SETUP.md)
- [Architecture](ARCHITECTURE.md)
