import json
import asyncio
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_google_cloud_sql_pg import PostgresEngine, PostgresVectorStore
from langchain_core.documents import Document

PROJECT_ID = "sapient-index-478801-f8"
AI_REGION = "us-central1" # Must match main.py

INSTANCE = "greenresolv-db"
DB_NAME = "tickets_db"
TABLE_NAME = "ticket_vectors"

async def ingest():
    engine = await PostgresEngine.afrom_instance(
        project_id=PROJECT_ID,
        region="us-central1",
        instance=INSTANCE,
        database=DB_NAME,
        user="postgres",
        password="hackathon_password_123"
    )

    await engine.ainit_vectorstore_table(
        table_name=TABLE_NAME,
        vector_size=768
    )

    # Create Embeddings in Central1
    embedding = VertexAIEmbeddings(
        model_name="text-embedding-004", 
        project=PROJECT_ID,
        location=AI_REGION
    )

    store = await PostgresVectorStore.create(
        engine=engine,
        table_name=TABLE_NAME,
        embedding_service=embedding
    )

    with open("past_tickets.json", "r") as f:
        data = json.load(f)
    
    docs = []
    for t in data:
        content = f"ISSUE: {t['issue_subject']}\nFIX: {t['resolution_summary']}\nCODE: {t['git_commit']['diff']}"
        docs.append(Document(page_content=content, metadata={"id": t['ticket_id']}))

    await store.aadd_documents(docs)
    print(f"Successfully ingested {len(docs)} tickets using US-CENTRAL1 model!")

if __name__ == "__main__":
    asyncio.run(ingest())
