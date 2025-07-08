from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    context_documents: List[Dict[str, Any]]
    question: str

class UploadResponse(BaseModel):
    file_id: str
    filename: str
    chunks_count: int
    message: str

class DeleteResponse(BaseModel):
    file_id: str
    message: str

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None 