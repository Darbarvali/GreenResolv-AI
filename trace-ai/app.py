import streamlit as st
import os
import json
from langchain_google_vertexai import ChatVertexAI, VertexAIEmbeddings
from langchain_google_cloud_sql_pg import PostgresEngine, PostgresVectorStore
from langchain.agents import tool, initialize_agent, AgentType
from langchain_core.documents import Document
from langchain.memory import ConversationBufferMemory
import datetime

# --- CONFIGURATION ---
PROJECT_ID = os.environ.get("GCP_PROJECT")
REGION = "us-central1"
INSTANCE = "greenresolv-db"
DB_NAME = "tickets_db"
TABLE_NAME = "ticket_vectors"

st.set_page_config(page_title="GreenResolv Agent", page_icon="🛡️")

# --- RESOURCES ---
@st.cache_resource
def get_db_engine():
    return PostgresEngine.from_instance(
        project_id=PROJECT_ID,
        region=REGION,
        instance=INSTANCE,
        database=DB_NAME,
        user="postgres",
        password="hackathon_password_123"
    )

@st.cache_resource
def get_vector_store():
    engine = get_db_engine()
    # 1. USE GECKO (Most Reliable for availability)
    embedding = VertexAIEmbeddings(
        model_name="text-embedding-005", 
        project=PROJECT_ID, 
        location=REGION
    )
    return PostgresVectorStore.create_sync(
        engine=engine,
        table_name=TABLE_NAME,
        embedding_service=embedding
    )

@st.cache_resource
def get_agent():
    store = get_vector_store()

    @tool
    def search_past_solutions(query: str):
        """Search the database for similar past resolved tickets."""
        try:
            docs = store.similarity_search(query, k=2)
            if not docs:
                return "No matching past tickets found."
            return "\n---\n".join([d.page_content for d in docs])
        except Exception as e:
            return f"Error: {str(e)}"

    # 2. USE CHAT-BISON (PaLM 2) for maximum stability
    llm = ChatVertexAI(
        model_name="gemini-2.0-flash-exp", 
        project=PROJECT_ID, 
        location=REGION,
        max_output_tokens=1024
    )
    
    memory = ConversationBufferMemory(
        memory_key="chat_history", 
        return_messages=True
    )
    
    return initialize_agent(
        [search_past_solutions], 
        llm, 
        agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True,
        memory=memory
    )

# --- REPORT GENERATOR ---
def generate_markdown(query, docs):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    md_content = f"# 🛡️ GreenResolv Incident Report\n**Date:** {timestamp}\n**Issue:** {query}\n\n---\n\n## 🔍 AI Analysis\n"
    
    for i, doc in enumerate(docs, 1):
        ticket_id = doc.metadata.get('id', 'Ref-00' + str(i))
        md_content += f"### 📄 Match #{i} (ID: {ticket_id})\n"
        md_content += f"```yaml\n{doc.page_content}\n```\n"
        md_content += f"\n---\n"
    
    return md_content

# --- ADMIN SIDEBAR ---
with st.sidebar:
    st.header("🔧 Admin Tools")
    if st.button("Reset Knowledge Base"):
        with st.status("Re-ingesting Data..."):
            engine = get_db_engine()
            embedding = VertexAIEmbeddings(model_name="textembedding-gecko@003", project=PROJECT_ID, location=REGION)
            
             
             

            engine.init_vectorstore_table(TABLE_NAME, 768)
            
            store = PostgresVectorStore.create_sync(engine, TABLE_NAME, embedding)
            
            if not os.path.exists("past_tickets.json"):
                 with open("past_tickets.json", "w") as f:
                     json.dump([{"ticket_id": "PG-2024-002", "issue_subject": "division by zero", "git_commit": {"diff": "+ NULLIF(val,0)"}}], f)

            with open("past_tickets.json", "r") as f:
                data = json.load(f)
            
            docs = []
            for t in data:
                content = f"ISSUE: {t['issue_subject']}\nFIX: {t.get('resolution_summary', 'See code')}\nCODE: {t['git_commit']['diff']}"
                docs.append(Document(page_content=content, metadata={"id": t['ticket_id']}))
            
            store.add_documents(docs)
            st.write(f"✅ Ingested {len(docs)} tickets!")

# --- MAIN CHAT UI ---
st.title("🛡️ GreenResolv AI")
st.caption(f"Running on PaLM 2 (US-Central1)")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! Describe your error, and I'll check our history for a fix."}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("Ex: Division by zero error..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    with st.chat_message("assistant"):
        agent = get_agent()
        response = agent.invoke({"input": prompt})
        st.write(response["output"])
        st.session_state.messages.append({"role": "assistant", "content": response["output"]})
        
        # Generate Report Button
        store = get_vector_store()
        relevant_docs = store.similarity_search(prompt, k=2)
        if relevant_docs:
            report = generate_markdown(prompt, relevant_docs)
            st.download_button("📥 Download Report (.md)", report, "greenresolv_report.md")
