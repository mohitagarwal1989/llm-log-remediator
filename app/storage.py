import time
import chromadb
from app.model import embed_text

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

async def store_exception_log(file_path, exception):
    emb = await embed_text(exception)
    logs_collection.add(
        ids=[f"{file_path}_{time.time()}"],
        documents=[exception],
        embeddings=emb,
        metadatas=[{"file": file_path}]
    )

async def find_fix_for_error(text):
    print("finding fix from error collection for", text)

    emb = await embed_text(text)

    result = error_collection.query(
        query_embeddings=emb,
        n_results=1,
        include=["metadatas", "distances"]
    )

    print("---", result)

    if not result:
        print("No result returned")
        return None

    metadatas = result.get("metadatas", [])
    distances = result.get("distances", [])

    if not metadatas or not metadatas[0] or not metadatas[0][0]:
        print("No metadata match found")
        return None

    if not distances or not distances[0] or not distances[0][0]:
        print("No distance info found")
        return None

    if distances[0][0] > 0.45:
        print("Match rejected due to distance:", distances[0][0])
        return None

    return metadatas[0][0].get("fix")


async def store_fix_in_kb(exception, fix):
    print("storing fix from llm to error collection")
    clean_fix = extract_fix_only(fix)
    document = f"Exception: {exception}\nFix: {clean_fix}"
    emb = await embed_text(exception)

    error_collection.add(
        ids=[f"{exception}_{time.time()}"],
        documents=[document],
        embeddings=emb,
        metadatas=[{"exception": exception, "fix": clean_fix}]
    )

def extract_fix_only(llm_output: str) -> str:
    if "Fix:" in llm_output:
        return llm_output.split("Fix:", 1)[1].strip()
    return llm_output.strip()    