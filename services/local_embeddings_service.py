import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any
import uuid
import numpy as np
from sentence_transformers import SentenceTransformer
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LocalEmbeddingsService:
    """Сервис для генерации эмбедингов с помощью локальной модели"""
    
    def __init__(self, model_name: str = "ai-forever/sbert_large_nlu_ru"):
        self.model_name = model_name
        self.model = None
        self.chroma_client = chromadb.PersistentClient(
            path="./chroma_db",
            settings=Settings(anonymized_telemetry=False)
        )
        self.default_collection = self.chroma_client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Инициализируем модель при создании сервиса
        self._load_model()
    
    def get_collection(self, collection_name: str):
        """Получает или создает коллекцию по имени"""
        return self.chroma_client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
    
    def _load_model(self):
        """Загружает модель для генерации эмбедингов"""
        try:
            logger.info(f"Загрузка модели {self.model_name}...")
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"Модель {self.model_name} успешно загружена")
        except Exception as e:
            logger.error(f"Ошибка загрузки модели {self.model_name}: {e}")
            raise Exception(f"Не удалось загрузить модель {self.model_name}: {str(e)}")
    
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Получает эмбединги для списка текстов с помощью локальной модели"""
        try:
            if not self.model:
                raise Exception("Модель не загружена")
            
            # Генерируем эмбединги
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            
            # Преобразуем в список списков float
            return embeddings.tolist()
            
        except Exception as e:
            raise Exception(f"Ошибка при получении эмбедингов: {str(e)}")
    
    def store_document(self, file_id: str, chunks: List[str], metadata: Dict[str, Any], collection_name: str = "documents"):
        """Сохраняет документ и его эмбединги в ChromaDB"""
        try:
            # Получаем эмбединги для всех чанков
            embeddings = self.get_embeddings(chunks)
            
            # Подготавливаем метаданные для каждого чанка
            metadatas = []
            ids = []
            
            for i, chunk in enumerate(chunks):
                chunk_metadata = metadata.copy()
                chunk_metadata.update({
                    "chunk_index": i,
                    "chunk_size": len(chunk),
                    "embedding_model": self.model_name,
                    "embedding_type": "local"
                })
                metadatas.append(chunk_metadata)
                ids.append(f"{file_id}_chunk_{i}")
            
            # Получаем нужную коллекцию
            collection = self.get_collection(collection_name)
            
            # Добавляем в ChromaDB
            collection.add(
                embeddings=embeddings,  # type: ignore
                documents=chunks,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Документ {file_id} сохранен с {len(chunks)} чанками в коллекции {collection_name}")
            
        except Exception as e:
            raise Exception(f"Ошибка при сохранении документа: {str(e)}")
    
    def search_similar(self, query: str, top_k: int = 5, collection_name: str = "documents") -> List[Dict[str, Any]]:
        """Ищет похожие документы по запросу"""
        try:
            # Получаем эмбединг для запроса
            query_embedding = self.get_embeddings([query])[0]
            
            # Получаем нужную коллекцию
            collection = self.get_collection(collection_name)
            
            # Ищем похожие документы
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            
            # Формируем результат
            similar_docs = []
            if results['documents'] and results['documents'][0]:
                # Ограничиваем количество результатов до top_k
                max_results = min(top_k, len(results['documents'][0]))
                for i in range(max_results):
                    similar_docs.append({
                        'document': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i] if results['metadatas'] and results['metadatas'][0] else {},
                        'distance': results['distances'][0][i] if results['distances'] and results['distances'][0] else 0.0
                    })
            
            return similar_docs
            
        except Exception as e:
            raise Exception(f"Ошибка при поиске похожих документов: {str(e)}")
    
    def delete_document(self, file_id: str, collection_name: str = "documents"):
        """Удаляет документ и его эмбединги из ChromaDB"""
        try:
            # Получаем нужную коллекцию
            collection = self.get_collection(collection_name)
            
            # Получаем все ID чанков для данного файла
            results = collection.get(
                where={"file_id": file_id}
            )
            
            if results['ids']:
                collection.delete(ids=results['ids'])
                logger.info(f"Документ {file_id} удален из ChromaDB коллекции {collection_name}")
            
        except Exception as e:
            raise Exception(f"Ошибка при удалении документа: {str(e)}")
    
    def clear_all(self, collection_name: str = "documents"):
        """Очищает все данные из ChromaDB"""
        try:
            self.chroma_client.delete_collection(name=collection_name)
            self.chroma_client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"Коллекция {collection_name} очищена")
        except Exception as e:
            raise Exception(f"Ошибка при очистке ChromaDB: {str(e)}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Возвращает информацию о модели"""
        return {
            "model_name": self.model_name,
            "model_loaded": self.model is not None,
            "embedding_type": "local"
        } 