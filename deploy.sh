#!/bin/bash
set -e

PROJECT="dayslegacy-ai-os"
REGION="europe-west1"
SERVICE="dayslegacy-app"
IMAGE="gcr.io/${PROJECT}/${SERVICE}"

echo "=== Build & push ==="
gcloud builds submit --tag "$IMAGE" --project "$PROJECT"

echo "=== Deploy Cloud Run ==="
gcloud run deploy "$SERVICE" \
  --image "$IMAGE" \
  --platform managed \
  --region "$REGION" \
  --project "$PROJECT" \
  --allow-unauthenticated \
  --port 8080 \
  --memory 512Mi \
  --cpu 1 \
  --set-env-vars "$(grep -v '^#' backend/.env | grep '=' | tr '\n' ',')"

echo "=== URL ==="
gcloud run services describe "$SERVICE" --region "$REGION" --project "$PROJECT" \
  --format="value(status.url)"
