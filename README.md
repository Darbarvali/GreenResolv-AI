# 🛡️ **GREENRESOLV AI — INTELLIGENT DEVELOPER SUPPORT AGENT**
### *BNB Marathon 2025 Submission*

Automating L1 Developer Support using Retrieval-Augmented Generation (RAG) on Google Cloud.

---

## 📑 **TABLE OF CONTENTS**
- [The Problem](#-the-problem)
- [The Solution](#-the-solution--greenresolv-ai)
- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Screenshots](#-screenshots)
- [Installation](#-installation--setup)
- [Deployment](#-deployment--cloud-run)
- [Challenges & Solutions](#-challenges--solutions)
- [Roadmap](#-roadmap)
- [Team](#-team)
- [License](#-license)

---

## 💡 **THE PROBLEM**
- 40% of developer support tickets are duplicates  
- LLM chatbots hallucinate due to missing historical fix context  
- Engineers waste time searching logs and past PRs  
- High MTTR and lack of structured incident memory  

---

## 🚀 **THE SOLUTION — GREENRESOLV AI**
GreenResolv is an AI-powered L1 Developer Support Agent that:
- Stores every resolved ticket
- Searches historical fixes using RAG + pgvector
- Retrieves exact logs, diffs, and explanations
- Synthesizes solutions using Vertex AI (Gemini/PaLM)

---

## ⭐ **FEATURES**
- 🧠 Vector search using **pgvector**  
- ⚡ Instant **Admin ingestion/reset**  
- 📝 Auto-generated **Markdown reports**  
- ☁️ Serverless on **Cloud Run**  
- 🔍 Accurate semantic retrieval  

---

## ⚙️ **ARCHITECTURE**
<img   height="1000" alt="image" src="https://github.com/user-attachments/assets/48f856b5-746e-4ab7-b2e7-98daabc16278" />
 



### Components
- **Frontend (US-East1):** Streamlit UI  
- **Brain (US-Central1):** Vertex AI (Gemini/PaLM)  
- **Memory:** Cloud SQL PostgreSQL 15 + pgvector  
- **Orchestration:** LangChain + Google PG Connector  

---

## 🛠️ **TECH STACK**

| Layer | Technology | Reason |
|-------|------------|--------|
| Frontend | Streamlit | Fast UI prototyping |
| Backend | Vertex AI | Reliable LLMs |
| Embeddings | Gecko 003 | High quality vectors |
| Vector DB | Cloud SQL + pgvector | Unified SQL + vector search |
| Connector | google-cloud-sql-pg | Secure IAM auth |
| Deploy | Cloud Run | Serverless |

---

## 📸 **SCREENSHOTS**
### 1. Chat Interface  
<img width="947" height="509" alt="image" src="https://github.com/user-attachments/assets/5811e187-a4be-4b93-9c4b-38b07d5ed4a5" />

### 2. Markdown Report  
<img width="836" height="450" alt="image" src="https://github.com/user-attachments/assets/913b3820-a87b-4d99-af9c-4f710a2d620e" />


---

## 🔧 **INSTALLATION & SETUP**

### 1️⃣ Clone Repo
```bash
git clone https://github.com/Darbarvali/GreenResolv-AI.git
cd GreenResolv-AI
```

### 2️⃣ Environment Setup
```bash
pip install -r requirements.txt
export PROJECT_ID="your-project-id"
```

### 3️⃣ Database Setup
```bash
gcloud sql instances create greenresolv-db     --database-version=POSTGRES_15     --tier=db-f1-micro     --region=us-central1     --root-password=yourpassword
```

### 4️⃣ Run Locally
```bash
streamlit run app.py
```

## 🚢 Deployment — Cloud Run
```bash
gcloud run deploy greenresolv-ui   --source .   --region us-central1   --allow-unauthenticated   --set-env-vars GCP_PROJECT=$PROJECT_ID
```

## 🚢 Deployment (Google Cloud Run)

We utilize a simplified deployment pipeline that builds the container and deploys it in one step:
```bash
gcloud run deploy greenresolv-ui \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GCP_PROJECT=$PROJECT_ID
```


## 🧠 Technical Challenges & Solutions

### 1️⃣ Regional Model Availability

Challenge: We initially deployed to us-east1, but discovered that specific Generative AI models (Gemini 1.5) were region-locked to us-central1 during the rollout phase, causing 404 Publisher Model Not Found errors.
Solution: We implemented a "Cross-Region" logic where the UI runs in us-east1 for user proximity, but hardcodes API calls to us-central1 for the LLM, ensuring 100% uptime.

### 2️⃣ Strict Schema Management

Challenge: The langchain-google-cloud-sql-pg library enforces a strict table schema (requiring a langchain_id UUID column). Legacy tables caused the app to crash with ValueError: Id column not found.
Solution: We built a "Self-Healing" ingestion pipeline. The Admin "Reset" button in the UI drops the existing table and lets the library strictly recreate it from scratch, ensuring schema compliance without manual SQL migration scripts.

## 🔮 What's Next?
- GitHub Webhooks  
- Multimodal screenshot support  
- Slack bot integration  
- Auto‑tuned retrieval

## 🌍 Live Deployment
**App URL:** [https://greenresolv-ui-12345.a.run.app](https://greenresolv-ui-172961617606.us-central1.run.app/)


Built with ❤️ for the BNB Marathon 2025.
