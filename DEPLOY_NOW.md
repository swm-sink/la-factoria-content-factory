# 🚀 DEPLOY AI CONTENT FACTORY - RIGHT NOW!

You have everything needed. Follow these steps to deploy in 5 minutes:

## Step 1: Set Your Project (30 seconds)
```bash
gcloud config set project ai-content-factory-460918
```

## Step 2: Enable Required APIs (2 minutes)
```bash
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com
```

## Step 3: Deploy! (3 minutes)
```bash
# From your project directory:
cd "/Users/smenssink/Documents/Github personal projects/ai-content-factory"

# One command deployment:
gcloud run deploy ai-content-factory \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars-from-file .env
```

## Step 4: Test Your Deployment (30 seconds)
```bash
# Get your service URL
SERVICE_URL=$(gcloud run services describe ai-content-factory \
  --region us-central1 --format 'value(status.url)')

# Test it works
curl $SERVICE_URL/healthz

# Show the URL
echo "Your app is live at: $SERVICE_URL"
```

## That's It! 🎉

Your AI Content Factory is now live on Google Cloud Run!

### Test Content Generation:
```bash
curl -X POST $SERVICE_URL/api/v1/content/generate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: FAKE_API_KEY_FOR_TESTING" \
  -d '{
    "syllabus_text": "Introduction to Machine Learning",
    "target_format": "all"
  }'
```

### What Just Happened:
- ✅ Your code was containerized automatically
- ✅ Pushed to Google Container Registry
- ✅ Deployed to a scalable Cloud Run service
- ✅ All your API keys from .env are configured
- ✅ HTTPS endpoint created automatically
- ✅ Auto-scaling configured (0 to 100 instances)

### Next Steps (Optional):
1. **View logs**: `gcloud run logs read --service ai-content-factory`
2. **Check metrics**: Visit [Cloud Run Console](https://console.cloud.google.com/run)
3. **Set up domain**: `gcloud run services update ai-content-factory --add-custom-audiences=your-domain.com`

### Cost Estimate:
- Cloud Run: ~$0.00024 per request
- Your API limits ensure max $5 per content generation
- With 100 requests/day = ~$5-10/day total

### Troubleshooting:
If deployment fails, run:
```bash
gcloud run deploy ai-content-factory \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars-from-file .env \
  --service-account cloud-tasks@ai-content-factory-460918.iam.gserviceaccount.com
```

**Your app is production-ready. Deploy now and iterate!** 🚀
