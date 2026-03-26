# 📝 Text Summarizer Agent

An AI agent built with **Google's Agent Development Kit (ADK)** and **Gemini 2.5 Flash**, deployed as a serverless HTTP service on **Google Cloud Run**.

This is my project submission for the *Building AI Agents with ADK* track — focused on agent structure, tool use, and production deployment.

---

## 🤖 What It Does

The agent accepts any block of text and returns a structured summary in a consistent format:
```
TL;DR:      One sentence capturing the core idea (≤ 25 words)
Key Points: 3–5 bullet points, one clear sentence each
Tone:       Single-word tone classification
```

---

## 🏗️ Architecture
```
User Request (HTTP)
      │
      ▼
 Cloud Run Service
      │
      ▼
 root_agent  (ADK Agent — gemini-2.5-flash)
      │
      ├── Tool: prepare_text_for_summary()
      │         Validates input, stores to agent state
      │
      └── LLM Instruction
                Reads RAW_TEXT from state
                Returns structured TL;DR + Key Points + Tone
```

---

## 📁 Project Structure
```
text_summarizer_agent/
├── agent.py           # Agent definition + tool
├── __init__.py        # ADK package marker
├── requirements.txt   # Dependencies
├── .env.example       # Config template (copy to .env)
├── .gitignore
└── README.md
```

---

## 🚀 Setup & Deployment

### Step 1 — Clone the repo
```bash
git clone https://github.com/farheen2604/text-summarizer-agent.git
cd text-summarizer-agent
```

### Step 2 — Create virtual environment and install dependencies
```bash
uv venv --python 3.12
source .venv/bin/activate
uv pip install -r requirements.txt
```

### Step 3 — Configure environment
```bash
PROJECT_ID=$(gcloud config get-value project)
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
SA_NAME=summarizer-cr-service

cat <<EOF > .env
PROJECT_ID=$PROJECT_ID
PROJECT_NUMBER=$PROJECT_NUMBER
SA_NAME=$SA_NAME
SERVICE_ACCOUNT=${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com
MODEL=gemini-2.5-flash
GOOGLE_GENAI_USE_VERTEXAI=1
GOOGLE_CLOUD_PROJECT=$PROJECT_ID
GOOGLE_CLOUD_LOCATION=us-central1
EOF

source .env
```

### Step 4 — Enable required APIs
```bash
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  aiplatform.googleapis.com \
  compute.googleapis.com
```

### Step 5 — Create service account and grant permissions
```bash
gcloud iam service-accounts create ${SA_NAME} \
    --display-name="Service Account for Text Summarizer Agent"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/aiplatform.user"
```

### Step 6 — Test locally
```bash
adk api_server --host 0.0.0.0 --port 8000 --allow_origins "*"
```

Open Web Preview on port 8000 in Cloud Shell and paste any text to test.

### Step 7 — Deploy to Cloud Run
```bash
source .env

uvx --from google-adk==1.14.0 \
adk deploy cloud_run \
  --project=$PROJECT_ID \
  --region=us-central1 \
  --service_name=text-summarizer-agent \
  --with_ui \
  . \
  -- \
  --service-account=$SERVICE_ACCOUNT
```

When prompted — type `y` for unauthenticated invocations.

---

## 🧪 Sample Test Inputs

**Test 1 — Technology:**
> Artificial intelligence is transforming the healthcare industry by enabling faster diagnosis, personalized treatment plans, and drug discovery. Machine learning models can now detect cancers from medical imaging with accuracy comparable to experienced radiologists. However, concerns around data privacy, algorithmic bias, and lack of regulatory frameworks remain significant barriers to widespread clinical adoption.

**Test 2 — Business:**
> Our Q3 revenue grew 18% year-over-year driven by strong performance in the enterprise segment. Customer acquisition costs dropped by 12% following the shift to product-led growth. However, churn in the SMB segment increased to 8.3%, which requires immediate attention from the customer success team.

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Agent Framework | Google ADK (google-adk 1.14.0) |
| LLM | Gemini 2.5 Flash via Vertex AI |
| Deployment | Google Cloud Run (serverless) |
| Container Build | Google Cloud Build + Artifact Registry |
| Auth | IAM Service Account (roles/aiplatform.user) |
| Language | Python 3.12 |

---

## 🧹 Cleanup
```bash
gcloud run services delete text-summarizer-agent --region=us-central1 --quiet
gcloud artifacts repositories delete cloud-run-source-deploy --location=us-central1 --quiet
```

---

## 📚 References

- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Vertex AI Gemini Models](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models)
- Codelab: [Build and deploy an ADK agent on Cloud Run](https://codelabs.developers.google.com/codelabs/production-ready-ai-with-gc/5-deploying-agents/deploy-an-adk-agent-to-cloud-run)
