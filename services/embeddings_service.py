import openai
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any
import uuid
from config import Config

class EmbeddingsService:
    def __init__(self):
        self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
        self.chroma_client = chromadb.PersistentClient(
            path="./chroma_db",
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.chroma_client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
    
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Получает эмбединги для списка текстов через OpenAI API"""
        try:
            response = self.client.embeddings.create(
                model="text-embedding-ada-002",
                input=texts
            )
            return [embedding.embedding for embedding in response.data]
        except Exception as e:
            raise Exception(f"Ошибка при получении эмбедингов: {str(e)}")
    
    def store_document(self, file_id: str, chunks: List[str], metadata: Dict[str, Any] = None):
        """Сохраняет документ в ChromaDB"""
        try:
            # Получаем эмбединги для всех чанков
            embeddings = self.get_embeddings(chunks)
            
            # Создаем уникальные ID для каждого чанка
            ids = [f"{file_id}_{i}" for i in range(len(chunks))]
            
            # Подготавливаем метаданные (упрощаем для ChromaDB)
            metadatas = []
            for i, chunk in enumerate(chunks):
                chunk_metadata = {
                    "file_id": file_id,
                    "chunk_index": str(i),
                    "chunk_size": str(len(chunk))
                }
                
                # Добавляем только простые метаданные из исходного файла
                if metadata:
                    # Копируем только простые поля
                    simple_fields = [
                        "filename", "file_size", "total_chunks", 
                        "file_type", "original_path", "txt_path", 
                        "conversion_method"
                    ]
                    for field in simple_fields:
                        if field in metadata:
                            value = metadata[field]
                            # Преобразуем в строку для ChromaDB
                            if isinstance(value, (dict, list)):
                                # Пропускаем сложные типы данных
                                continue
                            chunk_metadata[field] = str(value) if value is not None else ""
                
                metadatas.append(chunk_metadata)
            
            # Добавляем в коллекцию
            self.collection.add(
                embeddings=embeddings,
                documents=chunks,
                metadatas=metadatas,
                ids=ids
            )
            
        except Exception as e:
            raise Exception(f"Ошибка при сохранении документа в ChromaDB: {str(e)}")
    
    def search_similar(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Ищет похожие документы в ChromaDB"""
        try:
            # Получаем эмбединг для запроса
            query_embedding = self.get_embeddings([query])[0]
            
            # Ищем похожие документы
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            
            # Формируем результат
            documents = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    documents.append({
                        'document': doc,
                        'metadata': results['metadatas'][0][i] if results['metadatas'] and results['metadatas'][0] else {},
                        'distance': results['distances'][0][i] if results['distances'] and results['distances'][0] else 0
                    })
            
            return documents
            
        except Exception as e:
            raise Exception(f"Ошибка при поиске похожих документов: {str(e)}")
    
    def delete_document(self, file_id: str):
        """Удаляет документ из ChromaDB"""
        try:
            # Получаем все записи для данного file_id
            results = self.collection.get(
                where={"file_id": file_id}
            )
            
            if results['ids']:
                # Удаляем все записи
                self.collection.delete(ids=results['ids'])
                
        except Exception as e:
            raise Exception(f"Ошибка при удалении документа из ChromaDB: {str(e)}")
    
    def clear_all(self):
        """Очищает всю коллекцию ChromaDB"""
        try:
            # Удаляем всю коллекцию
            self.chroma_client.delete_collection(name="documents")
            
            # Создаем новую пустую коллекцию
            self.collection = self.chroma_client.create_collection(
                name="documents",
                metadata={"hnsw:space": "cosine"}
            )
                
        except Exception as e:
            raise Exception(f"Ошибка при очистке ChromaDB: {str(e)}") 