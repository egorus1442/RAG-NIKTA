from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class QueryRequest(BaseModel):
    question: str
    include_context: bool = True  # Новая опция для включения/исключения контекста

class QueryResponse(BaseModel):
    answer: str
    context_documents: Optional[List[Dict[str, Any]]] = None
    question: str
    tokens: Optional[Dict[str, int]] = None  # Информация о токенах

class UploadResponse(BaseModel):
    file_id: str
    filename: str
    chunks_count: int
    message: str
    processing_info: Dict[str, Any] = {}  # Информация о обработке

class DeleteResponse(BaseModel):
    file_id: str
    message: str

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None 