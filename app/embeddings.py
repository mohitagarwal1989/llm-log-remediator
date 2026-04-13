import asyncio
from concurrent.futures import ThreadPoolExecutor
from sentence_transformers import SentenceTransformer

_executor = ThreadPoolExecutor(max_workers=4)
_model = None

async def load_model():
    global _model
    loop = asyncio.get_event_loop()
    _model = await loop.run_in_executor(
        _executor, SentenceTransformer, "all-MiniLM-L6-v2"
    )

async def embed(text: str):
    if _model is None:
        raise RuntimeError("Embedding model not loaded")
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, _model.encode, [text])