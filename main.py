import os
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Form, Query
from fastapi.responses import JSONResponse
from typing import List

from config import Config
from auth import verify_token
from models import (
    QueryRequest, QueryResponse, UploadResponse, DeleteResponse, 
    ErrorResponse, ApiKeyRequest, ApiKeyResponse, 
    EmbeddingTypeRequest, EmbeddingTypeResponse,
    CollectionRequest, CollectionResponse, ListCollectionsResponse
)
from utils.text_extractor import TextExtractor
from services.embeddings_factory import EmbeddingsFactory
from services.llm_service import LLMService
from services.file_processor import FileProcessor
from services.collections_service import CollectionsService

app = FastAPI(
    title="RAG API",
    description="Retrieval-Augmented Generation API с поддержкой загрузки документов и генерации ответов",
    version="1.0.0"
)

# Инициализируем сервисы
embeddings_service = EmbeddingsFactory.create_embeddings_service()
llm_service = LLMService()
file_processor = FileProcessor(Config.UPLOAD_DIR)
collections_service = CollectionsService()

@app.post("/upload", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    collection: str = Query(..., description="Название коллекции"),
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
        embeddings_service.store_document(file_data['file_id'], chunks, file_metadata, collection)
        
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
    collection: str = Query(..., description="Название коллекции"),
    token: str = Depends(verify_token)
):
    """Удаляет файл и его эмбединги"""
    try:
        # Удаляем из ChromaDB
        embeddings_service.delete_document(file_id, collection)
        
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
        embeddings_service.clear_all("documents")  # Очищаем только дефолтную коллекцию
        
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
    collection: str = Query(..., description="Название коллекции"),
    token: str = Depends(verify_token)
):
    """Выполняет поиск по документам и генерирует ответ"""
    try:
        # Ищем похожие документы
        similar_docs = embeddings_service.search_similar(
            request.question, 
            top_k=Config.TOP_K,
            collection_name=collection
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

@app.post("/set-openrouter-key", response_model=ApiKeyResponse)
async def set_openrouter_api_key(
    request: ApiKeyRequest,
    token: str = Depends(verify_token)
):
    """Устанавливает OPENROUTER_API_KEY для использования в LLM сервисе"""
    try:
        # Проверяем, что API ключ не пустой
        if not request.api_key or request.api_key.strip() == "":
            raise HTTPException(status_code=400, detail="API ключ не может быть пустым")
        
        # Устанавливаем новый API ключ в конфигурацию
        Config.OPENROUTER_API_KEY = request.api_key.strip()
        
        # Обновляем API ключ в LLM сервисе
        llm_service.api_key = Config.OPENROUTER_API_KEY
        
        # Опционально: можно сохранить в .env файл для персистентности
        # Но для простоты пока просто обновляем в памяти
        
        return ApiKeyResponse(
            message="OPENROUTER_API_KEY успешно обновлен",
            status="success"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/openrouter-key-status", response_model=ApiKeyResponse)
async def get_openrouter_key_status(
    token: str = Depends(verify_token)
):
    """Проверяет статус OPENROUTER_API_KEY"""
    try:
        if Config.OPENROUTER_API_KEY:
            return ApiKeyResponse(
                message="OPENROUTER_API_KEY установлен",
                status="configured"
            )
        else:
            return ApiKeyResponse(
                message="OPENROUTER_API_KEY не установлен",
                status="not_configured"
            )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/set-embedding-type", response_model=EmbeddingTypeResponse)
async def set_embedding_type(
    request: EmbeddingTypeRequest,
    token: str = Depends(verify_token)
):
    """Устанавливает тип эмбедингов (OpenAI или Local)"""
    try:
        embedding_type = request.embedding_type.lower()
        
        # Проверяем, что тип поддерживается
        if embedding_type not in EmbeddingsFactory.get_available_types():
            raise HTTPException(
                status_code=400, 
                detail=f"Неподдерживаемый тип эмбедингов: {embedding_type}. Доступные типы: {EmbeddingsFactory.get_available_types()}"
            )
        
        # Обновляем конфигурацию
        Config.EMBEDDING_TYPE = embedding_type
        
        # Пересоздаем сервис эмбедингов
        global embeddings_service
        embeddings_service = EmbeddingsFactory.create_embeddings_service()
        
        return EmbeddingTypeResponse(
            message=f"Тип эмбедингов успешно изменен на {embedding_type}",
            status="success",
            current_type=embedding_type,
            available_types=EmbeddingsFactory.get_available_types()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/embedding-type-status", response_model=EmbeddingTypeResponse)
async def get_embedding_type_status(
    token: str = Depends(verify_token)
):
    """Проверяет текущий тип эмбедингов"""
    try:
        current_type = EmbeddingsFactory.get_current_type()
        
        return EmbeddingTypeResponse(
            message=f"Текущий тип эмбедингов: {current_type}",
            status="success",
            current_type=current_type,
            available_types=EmbeddingsFactory.get_available_types()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/create-collection", response_model=CollectionResponse)
async def create_collection(
    request: CollectionRequest,
    token: str = Depends(verify_token)
):
    try:
        collections_service.create_collection(request.collection_name)
        return CollectionResponse(message="Коллекция успешно создана", status="success")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/delete-collection", response_model=CollectionResponse)
async def delete_collection(
    request: CollectionRequest,
    token: str = Depends(verify_token)
):
    try:
        collections_service.delete_collection(request.collection_name)
        return CollectionResponse(message="Коллекция успешно удалена", status="success")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/list-collections", response_model=ListCollectionsResponse)
async def list_collections(token: str = Depends(verify_token)):
    try:
        collections = collections_service.list_collections()
        return ListCollectionsResponse(collections=collections, status="success")
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