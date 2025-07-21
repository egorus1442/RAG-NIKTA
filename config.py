import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    API_TOKEN = os.getenv("API_TOKEN")
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
    TOP_K = int(os.getenv("TOP_K", "5"))
    
    # Настройки для эмбедингов
    EMBEDDING_TYPE = os.getenv("EMBEDDING_TYPE", "openai")  # "openai" или "local"
    LOCAL_MODEL_NAME = os.getenv("LOCAL_MODEL_NAME", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    
    # Создаем директорию для загрузок если её нет
    os.makedirs(UPLOAD_DIR, exist_ok=True) 