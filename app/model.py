import asyncio
from concurrent.futures import ThreadPoolExecutor
from sentence_transformers import SentenceTransformer

_executor = ThreadPoolExecutor(max_workers=4)
_embed_model = None

async def load_model():
    global _embed_model
    loop = asyncio.get_event_loop()
    _embed_model = await loop.run_in_executor(
        _executor, SentenceTransformer, "all-MiniLM-L6-v2"
    )

async def embed_text(text: str):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        _executor, _embed_model.encode, [text]
    )