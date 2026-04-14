from pydantic import BaseModel
from typing import List, Any

class QueryResponse(BaseModel):
    ids: List[Any]
    documents: List[Any]
    metadatas: List[Any]