import os
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import List

from config import Config
from auth import verify_token
from models import QueryRequest, QueryResponse, UploadResponse, DeleteResponse, ErrorResponse
from utils.text_extractor import TextExtractor
from services.embeddings_service import EmbeddingsService
from services.llm_service import LLMService
from services.file_processor import FileProcessor

app = FastAPI(
    title="RAG API",
    description="Retrieval-Augmented Generation API с поддержкой загрузки документов и генерации ответов",
    version="1.0.0"
)

# Инициализируем сервисы
embeddings_service = EmbeddingsService()
llm_service = LLMService()
file_processor = FileProcessor(Config.UPLOAD_DIR)

@app.post("/upload", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    token: str = Depends(verify_token)
):
    """Загружает файл, конвертирует в txt и сохраняет эмбединги"""
    try:
        # Проверяем, что файл не пустой
        if not file.filename:
            raise HTTPException(status_code=400, detail="Имя файла не может быть пустым")
        
        # Читаем содержимое файла
        content = await file.read()
        
        # Обрабатываем файл через FileProcessor
        file_data = file_processor.process_uploaded_file(content, file.filename)
        
        # Разбиваем текст на чанки
        chunks = TextExtractor.chunk_text(
            file_data['text'], 
            Config.CHUNK_SIZE, 
            Config.CHUNK_OVERLAP
        )
        
        # Подготавливаем метаданные для сохранения
        file_metadata = {
            "filename": file_data['original_filename'],
            "file_size": file_data['file_size'],
            "total_chunks": len(chunks),
            "file_type": file_data['file_type'],
            "original_path": file_data['original_path'],
            "txt_path": file_data['txt_path'],
            "extraction_metadata": file_data['extraction_metadata']
        }
        
        # Сохраняем эмбединги
        embeddings_service.store_document(file_data['file_id'], chunks, file_metadata)
        
        return UploadResponse(
            file_id=file_data['file_id'],
            filename=file_data['original_filename'],
            chunks_count=len(chunks),
            message="Файл успешно загружен, конвертирован в txt и обработан"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
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
        
        # Удаляем файлы с диска
        deleted = file_processor.delete_file_versions(file_id)
        
        if not deleted:
            raise HTTPException(status_code=404, detail="Файл не найден")
        
        return DeleteResponse(
            file_id=file_id,
            message="Файл и все связанные версии успешно удалены"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/clear-all", response_model=DeleteResponse)
async def clear_all_data(
    token: str = Depends(verify_token)
):
    """Удаляет все файлы и данные из системы"""
    try:
        # Очищаем ChromaDB
        embeddings_service.clear_all()
        
        # Очищаем папку uploads
        import shutil
        import os
        
        upload_dir = Config.UPLOAD_DIR
        if os.path.exists(upload_dir):
            for filename in os.listdir(upload_dir):
                file_path = os.path.join(upload_dir, filename)
                if os.path.isfile(file_path) and filename != '.gitkeep':
                    os.remove(file_path)
        
        return DeleteResponse(
            file_id="all",
            message="Все файлы и данные успешно удалены из системы"
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
        response_data = llm_service.generate_response(request.question, similar_docs)
        answer = response_data["answer"]
        tokens = response_data["tokens"]
        
        # Формируем ответ в зависимости от опции include_context
        if request.include_context:
            return QueryResponse(
                answer=answer,
                context_documents=similar_docs,
                question=request.question,
                tokens=tokens
            )
        else:
            return QueryResponse(
                answer=answer,
                context_documents=None,
                question=request.question,
                tokens=tokens
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