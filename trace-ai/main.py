import os
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_google_vertexai import ChatVertexAI, VertexAIEmbeddings
from langchain_google_cloud_sql_pg import PostgresEngine, PostgresVectorStore
from langchain.agents import tool, initialize_agent, AgentType

app = FastAPI(title="GreenResolv API")

# --- CONFIG ---
PROJECT_ID = os.environ.get("GCP_PROJECT")
# FORCE AI TO CENTRAL1 (Where we verified it works)
AI_REGION = "us-central1" 

INSTANCE = "greenresolv-db"
DB_NAME = "tickets_db"
TABLE_NAME = "ticket_vectors"

# --- GLOBAL RESOURCES ---
engine = PostgresEngine.from_instance(
    project_id=PROJECT_ID,
    region="us-central1",  # Your DB is in central1
    instance=INSTANCE,
    database=DB_NAME,
    user="postgres",
    password="hackathon_password_123"
)

# FORCE EMBEDDINGS TO CENTRAL1
embedding = VertexAIEmbeddings(
    model_name="text-embedding-004",
    project=PROJECT_ID,
    location=AI_REGION
)

vector_store = PostgresVectorStore.create_sync(
    engine=engine,
    table_name=TABLE_NAME,
    embedding_service=embedding
)

# --- TOOLS & AGENT ---
@tool
def search_past_solutions(query: str):
    """Search the Cloud SQL database for similar past resolved tickets."""
    try:
        docs = vector_store.similarity_search(query, k=2)
        if not docs:
            return "No matching past tickets found."
        return "\n---\n".join([d.page_content for d in docs])
    except Exception as e:
        return f"Error searching database: {str(e)}"

# FORCE GEMINI TO CENTRAL1 & USE STABLE MODEL 1.0 PRO
llm = ChatVertexAI(
    model_name="gemini-1.0-pro",
    project=PROJECT_ID,
    location=AI_REGION
)

tools = [search_past_solutions]

agent = initialize_agent(
    tools, 
    llm, 
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# --- API ENDPOINTS ---
class TicketQuery(BaseModel):
    query: str

@app.post("/resolve")
def resolve_ticket(ticket: TicketQuery):
    response = agent.invoke(ticket.query)
    return {"solution": response['output']}
