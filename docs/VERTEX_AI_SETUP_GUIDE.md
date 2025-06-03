# Vertex AI Setup Guide for AI Content Factory

**Last Updated**: June 3, 2025

## Prerequisites

1. **Google Cloud Project**: You need an active GCP project with billing enabled
2. **Vertex AI API**: Must be enabled in your project
3. **Authentication**: Either gcloud CLI or service account key

## Step 1: Enable Required APIs

```bash
# Set your project ID
export GCP_PROJECT_ID="your-project-id"
gcloud config set project $GCP_PROJECT_ID

# Enable required APIs
gcloud services enable aiplatform.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable firestore.googleapis.com
gcloud services enable cloudtasks.googleapis.com
gcloud services enable run.googleapis.com
```

## Step 2: Authentication Setup

You have two options:

### Option A: Local Development with gcloud (Recommended for testing)

```bash
# Authenticate with your Google account
gcloud auth application-default login

# Verify authentication
gcloud auth application-default print-access-token
```

### Option B: Service Account (Required for production)

```bash
# Create a service account
gcloud iam service-accounts create ai-content-factory-sa \
    --display-name="AI Content Factory Service Account"

# Get the service account email
export SA_EMAIL="ai-content-factory-sa@${GCP_PROJECT_ID}.iam.gserviceaccount.com"

# Grant necessary roles
gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/secretmanager.secretAccessor"

gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/datastore.user"

gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/cloudtasks.enqueuer"

# Create and download key
gcloud iam service-accounts keys create key.json \
    --iam-account=$SA_EMAIL

# Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/key.json"
```

## Step 3: Update Environment Variables

Update your `.env` file:

```env
# GCP Configuration
GCP_PROJECT_ID=your-project-id
GCP_LOCATION=us-central1

# Model Configuration
GEMINI_MODEL_NAME=gemini-1.5-flash

# For production, set this to your service account key path
# GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json

# API Keys (still needed for other services)
API_KEY=your-api-key-for-app-access
ELEVENLABS_API_KEY=your-elevenlabs-key

# Optional: If using Secret Manager
# Remove these and they'll be loaded from Secret Manager
# API_KEY=
# ELEVENLABS_API_KEY=
```

## Step 4: Test Vertex AI Connection

Create a test script to verify your setup:

```python
# test_vertex_ai.py
import vertexai
from vertexai.generative_models import GenerativeModel
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Vertex AI
project_id = os.getenv("GCP_PROJECT_ID")
location = os.getenv("GCP_LOCATION", "us-central1")

vertexai.init(project=project_id, location=location)

# Test the model
model = GenerativeModel("gemini-1.5-flash")
response = model.generate_content("Hello, please respond with a simple greeting.")

print(f"✅ Vertex AI is working!")
print(f"Response: {response.text}")
```

Run the test:
```bash
python test_vertex_ai.py
```

## Step 5: Deploy to Cloud Run

For Cloud Run deployment, the service account is automatically provided:

```bash
# Deploy to Cloud Run
gcloud run deploy ai-content-factory \
    --image gcr.io/${GCP_PROJECT_ID}/ai-content-factory:latest \
    --platform managed \
    --region us-central1 \
    --service-account $SA_EMAIL \
    --set-env-vars "GCP_PROJECT_ID=${GCP_PROJECT_ID},GCP_LOCATION=us-central1"
```

## Troubleshooting

### Error: "Could not automatically determine credentials"

**Solution**: Run `gcloud auth application-default login` or set `GOOGLE_APPLICATION_CREDENTIALS`

### Error: "Permission denied"

**Solution**: Ensure your service account has the `roles/aiplatform.user` role:
```bash
gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/aiplatform.user"
```

### Error: "API not enabled"

**Solution**: Enable the Vertex AI API:
```bash
gcloud services enable aiplatform.googleapis.com
```

## Cost Considerations

Vertex AI pricing for Gemini models (as of June 2025):
- **Gemini 1.5 Flash**: $0.00035 per 1K input tokens, $0.00105 per 1K output tokens
- **Gemini 1.5 Pro**: $0.00125 per 1K input tokens, $0.00375 per 1K output tokens

Estimated costs for your use case:
- Average request: ~2K input + 3K output tokens
- Cost per request: ~$0.004 (Gemini 1.5 Flash)
- 1000 requests/day: ~$4/day or ~$120/month

## Security Best Practices

1. **Never commit service account keys** to Git
2. **Use Secret Manager** for production API keys
3. **Rotate service account keys** regularly
4. **Use least privilege** - only grant necessary permissions
5. **Enable audit logging** for all API calls

## Next Steps

1. Complete the authentication setup above
2. Run the test script to verify connectivity
3. Test the application locally:
   ```bash
   docker compose up
   ```
4. Test content generation:
   ```bash
   curl -X POST http://localhost:8081/api/v1/content/generate \
     -H "Content-Type: application/json" \
     -H "X-API-Key: FAKE_API_KEY_FOR_TESTING" \
     -d '{
       "syllabus_text": "Introduction to Python Programming",
       "target_format": "all"
     }'
   ```

## Support

If you encounter issues:
1. Check the [Vertex AI documentation](https://cloud.google.com/vertex-ai/docs)
2. Verify your project has billing enabled
3. Ensure all required APIs are enabled
4. Check service account permissions
