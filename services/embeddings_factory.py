from typing import Union
from config import Config
from services.embeddings_service import EmbeddingsService
from services.local_embeddings_service import LocalEmbeddingsService

class EmbeddingsFactory:
    """Фабрика для создания сервисов эмбедингов"""
    
    @staticmethod
    def create_embeddings_service() -> Union[EmbeddingsService, LocalEmbeddingsService]:
        """Создает сервис эмбедингов в зависимости от настроек"""
        embedding_type = Config.EMBEDDING_TYPE.lower()
        
        if embedding_type == "local":
            return LocalEmbeddingsService(Config.LOCAL_MODEL_NAME)
        elif embedding_type == "openai":
            return EmbeddingsService()
        else:
            raise ValueError(f"Неизвестный тип эмбедингов: {embedding_type}. Поддерживаемые типы: 'openai', 'local'")
    
    @staticmethod
    def get_available_types() -> list:
        """Возвращает список доступных типов эмбедингов"""
        return ["openai", "local"]
    
    @staticmethod
    def get_current_type() -> str:
        """Возвращает текущий тип эмбедингов"""
        return Config.EMBEDDING_TYPE.lower() 