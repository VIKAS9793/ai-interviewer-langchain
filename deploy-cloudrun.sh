#!/bin/bash
# Deploy ADK Interviewer to Google Cloud Run
# Optimized for Free Tier

set -e

# Configuration
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-your-project-id}"
REGION="${GCP_REGION:-us-central1}"
SERVICE_NAME="ai-interviewer-adk"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "🚀 Deploying AI Interviewer (ADK) to Cloud Run"
echo "=============================================="
echo "Project: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo "Service: ${SERVICE_NAME}"
echo ""

# Step 1: Build container
echo "📦 Building container..."
docker build -f Dockerfile.adk -t ${IMAGE_NAME}:latest .

# Step 2: Push to GCR
echo "⬆️  Pushing to Container Registry..."
docker push ${IMAGE_NAME}:latest

# Step 3: Deploy to Cloud Run
echo "🌐 Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME}:latest \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --memory 256Mi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 1 \
    --timeout 300 \
    --set-secrets "GOOGLE_API_KEY=google-api-key:latest"

# Step 4: Get URL
echo ""
echo "✅ Deployment complete!"
echo ""
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region ${REGION} --format 'value(status.url)')
echo "🔗 Service URL: ${SERVICE_URL}"
echo ""
echo "To view logs:"
echo "  gcloud run logs read ${SERVICE_NAME} --region ${REGION}"
