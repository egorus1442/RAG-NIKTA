import os
import uuid
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import List

from config import Config
from auth import verify_token
from models import QueryRequest, QueryResponse, UploadResponse, DeleteResponse, ErrorResponse
from utils.text_extractor import TextExtractor
from services.embeddings_service import EmbeddingsService
from services.llm_service import LLMService

app = FastAPI(
    title="RAG API",
    description="Retrieval-Augmented Generation API с поддержкой загрузки документов и генерации ответов",
    version="1.0.0"
)

# Инициализируем сервисы
embeddings_service = EmbeddingsService()
llm_service = LLMService()

@app.post("/upload", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    token: str = Depends(verify_token)
):
    """Загружает файл, извлекает текст и сохраняет эмбединги"""
    try:
        # Проверяем поддерживаемые форматы
        if not file.filename:
            raise HTTPException(status_code=400, detail="Имя файла не может быть пустым")
            
        allowed_extensions = {'.pdf', '.docx', '.txt'}
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Неподдерживаемый формат файла. Поддерживаемые форматы: {', '.join(allowed_extensions)}"
            )
        
        # Генерируем уникальный ID файла
        file_id = str(uuid.uuid4())
        file_path = os.path.join(Config.UPLOAD_DIR, f"{file_id}_{file.filename}")
        
        # Сохраняем файл
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Извлекаем текст
        text = TextExtractor.extract_text(file_path)
        
        # Разбиваем на чанки
        chunks = TextExtractor.chunk_text(
            text, 
            chunk_size=Config.CHUNK_SIZE, 
            overlap=Config.CHUNK_OVERLAP
        )
        
        # Сохраняем эмбединги
        metadata = {
            "filename": file.filename,
            "file_size": len(content),
            "total_chunks": len(chunks)
        }
        
        embeddings_service.store_document(file_id, chunks, metadata)
        
        return UploadResponse(
            file_id=file_id,
            filename=file.filename or "unknown",
            chunks_count=len(chunks),
            message="Файл успешно загружен и обработан"
        )
        
    except Exception as e:
        # Удаляем файл в случае ошибки
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/file/{file_id}", response_model=DeleteResponse)
async def delete_file(
    file_id: str,
    token: str = Depends(verify_token)
):
    """Удаляет файл и его эмбединги"""
    try:
        # Удаляем из ChromaDB
        embeddings_service.delete_document(file_id)
        
        # Удаляем файл с диска
        upload_dir = Config.UPLOAD_DIR
        for filename in os.listdir(upload_dir):
            if filename.startswith(file_id):
                file_path = os.path.join(upload_dir, filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
                break
        
        return DeleteResponse(
            file_id=file_id,
            message="Файл успешно удален"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query", response_model=QueryResponse)
async def query_documents(
    request: QueryRequest,
    token: str = Depends(verify_token)
):
    """Выполняет поиск по документам и генерирует ответ"""
    try:
        # Ищем похожие документы
        similar_docs = embeddings_service.search_similar(
            request.question, 
            top_k=Config.TOP_K
        )
        
        # Генерируем ответ
        answer = llm_service.generate_response(request.question, similar_docs)
        
        return QueryResponse(
            answer=answer,
            context_documents=similar_docs,
            question=request.question
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Проверка состояния API"""
    return {"status": "healthy", "message": "RAG API работает"}

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(error=exc.detail).dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(error="Внутренняя ошибка сервера", detail=str(exc)).dict()
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 