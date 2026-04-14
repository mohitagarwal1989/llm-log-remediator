from fastapi import FastAPI, Query
from sentence_transformers import SentenceTransformer
import chromadb

from api.schemas import QueryResponse

app = FastAPI(title="LLM Log Remediator API")

# -------------------------------------------------
# Chroma clients (shared with worker)
# -------------------------------------------------
log_client = chromadb.PersistentClient(path="log_chroma_db")
logs_collection = log_client.get_or_create_collection(
    name="log_exceptions",
    metadata={"hnsw:space": "cosine"}
)

kb_client = chromadb.PersistentClient(path="error_knowledge_db")
error_collection = kb_client.get_or_create_collection(
    name="error_knowledge_base",
    metadata={"hnsw:space": "cosine"}
)

embed_model = None

# -------------------------------------------------
# Startup hook
# -------------------------------------------------
@app.on_event("startup")
def load_model():
    global embed_model
    embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# -------------------------------------------------
# Query logged exceptions
# -------------------------------------------------
@app.get("/query", response_model=QueryResponse)
def query_logs(search: str = Query(..., description="Search exception text")):
    emb = embed_model.encode([search]).tolist()
    result = logs_collection.query(query_embeddings=emb)

    return QueryResponse(
        ids=result.get("ids", []),
        documents=result.get("documents", []),
        metadatas=result.get("metadatas", [])
    )

# -------------------------------------------------
# Get all logged exceptions
# -------------------------------------------------
@app.get("/logs", response_model=QueryResponse)
def get_all_logs():
    data = logs_collection.get(include=["documents", "metadatas"])

    return QueryResponse(
        ids=data.get("ids", []),
        documents=data.get("documents", []),
        metadatas=data.get("metadatas", [])
    )

# -------------------------------------------------
# Get error knowledge base
# -------------------------------------------------
@app.get("/knowledge", response_model=QueryResponse)
def get_knowledge_base():
    data = error_collection.get(include=["documents", "metadatas"])

    return QueryResponse(
        ids=data.get("ids", []),
        documents=data.get("documents", []),
        metadatas=data.get("metadatas", [])
    )

# -------------------------------------------------
# Clear knowledge base
# -------------------------------------------------
@app.delete("/knowledge")
def clear_knowledge_base():
    data = error_collection.get(include=[])
    ids = data.get("ids", [])

    if not ids:
        return {"status": "No records to delete"}

    error_collection.delete(ids=ids)
    return {"status": f"Deleted {len(ids)} records"}

# -------------------------------------------------
# Clear log store
# -------------------------------------------------
@app.delete("/logs")
def clear_logs():
    data = logs_collection.get(include=[])
    ids = data.get("ids", [])

    if not ids:
        return {"status": "No records to delete"}

    logs_collection.delete(ids=ids)
    return {"status": f"Deleted {len(ids)} records"}