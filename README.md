🛡️ GreenResolv AI: Intelligent Developer Support Agent

Project Saadhna / BNB Marathon 2025 Submission

Automating L1 Developer Support using Retrieval-Augmented Generation (RAG) on Google Cloud.

💡 The Problem

In the fast-paced world of Web3 and Cloud development, Developer Relations (DevRel) teams are overwhelmed.

Repetitive Queries: 40% of support tickets are duplicates (e.g., "Transaction failed", "Division by zero").

Loss of Context: Standard chatbots hallucinate because they don't know the history of how a bug was actually fixed in the repo.

High MTTR: Engineers waste hours searching through old logs to find previous solutions.

🚀 The Solution

GreenResolv is an AI Agent that "remembers" every past resolved ticket.

It uses a RAG (Retrieval-Augmented Generation) architecture to semantic search through historical logs stored in Cloud SQL, retrieves the exact technical fix (including code diffs), and uses Vertex AI to synthesize a solution for the user.

Key Features:

🧠 Contextual Memory: Uses pgvector to understand the meaning of an error, not just keywords.

🛠️ Automated Ingestion: Admin dashboard to ingest/reset knowledge base from JSON logs instantly.

📄 Report Generation: Auto-generates downloadable Markdown (.md) incident reports for documentation.

☁️ Cloud Native: Fully serverless architecture on Google Cloud Run.

⚙️ Architecture

(Replace this image link with your actual diagram)

The system follows a "Split-Brain" Architecture to optimize for Model Availability vs. User Latency:

Frontend (US-East1): A Streamlit application hosted on Cloud Run handles user interaction.

The Brain (US-Central1): Logic is routed to us-central1 to access high-availability Foundation Models (PaLM 2 / Gemini).

The Memory (US-Central1): A Cloud SQL (PostgreSQL 15) instance stores vector embeddings using the pgvector extension.

Orchestration: LangChain connects the user query to the vector store and the LLM.

🛠️ Tech Stack

Component

Technology

Why we chose it?

Frontend

Streamlit

Rapid UI development with built-in chat interfaces.

LLM

Vertex AI (PaLM 2 / Gemini)

Enterprise-grade reliability and low latency.

Embeddings

Gecko (textembedding-gecko@003)

Stable, high-dimensional vector generation.

Vector DB

Cloud SQL + pgvector

Combines relational data with vector search in one managed service.

Connector

langchain-google-cloud-sql-pg

Google's native library for secure IAM-based connections.

Deploy

Cloud Run

Scale-to-zero serverless deployment.

📸 Screenshots

1. The Chat Interface
(Insert screenshot of the agent solving a division by zero error)

2. The Generated Report
(Insert screenshot of the downloaded .md file)

🔧 Installation & Setup

Prerequisites

Google Cloud Project with Billing Enabled.

gcloud CLI installed.

Python 3.11+.

1. Clone the Repository

git clone [https://github.com/Darbarvali/GreenResolv-AI.git](https://github.com/Darbarvali/GreenResolv-AI.git)
cd GreenResolv-AI


2. Environment Setup

# Install dependencies
pip install -r requirements.txt

# Set Google Cloud Project ID
export PROJECT_ID="your-project-id"


3. Database Setup

Create a Cloud SQL instance with pgvector support:

gcloud sql instances create greenresolv-db \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=us-central1 \
    --root-password=yourpassword


4. Run Locally

streamlit run app.py


🚢 Deployment (Google Cloud Run)

We utilize a simplified deployment pipeline that builds the container and deploys it in one step:

gcloud run deploy greenresolv-ui \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GCP_PROJECT=$PROJECT_ID


🧠 Technical Challenges & Solutions

1. Regional Model Availability

Challenge: We initially deployed to us-east1, but discovered that specific Generative AI models (Gemini 1.5) were region-locked to us-central1 during the rollout phase, causing 404 Publisher Model Not Found errors.
Solution: We implemented a "Cross-Region" logic where the UI runs in us-east1 for user proximity, but hardcodes API calls to us-central1 for the LLM, ensuring 100% uptime.

2. Strict Schema Management

Challenge: The langchain-google-cloud-sql-pg library enforces a strict table schema (requiring a langchain_id UUID column). Legacy tables caused the app to crash with ValueError: Id column not found.
Solution: We built a "Self-Healing" ingestion pipeline. The Admin "Reset" button in the UI drops the existing table and lets the library strictly recreate it from scratch, ensuring schema compliance without manual SQL migration scripts.

🔮 What's Next?

GitHub Webhooks: Automatically ingest new issues when they are closed on GitHub.

Multimodal Support: Allow users to upload screenshots of their error logs using Gemini 1.5 Pro.

Slack Integration: Deploy the agent as a Slack Bot for internal teams.

👥 Team

Darbarvali - Lead Developer / Cloud Architect

Built with ❤️ for the BNB Marathon 2025.
