import requests
import json
from typing import List, Dict, Any
from config import Config

class LLMService:
    def __init__(self):
        self.api_key = Config.OPENROUTER_API_KEY
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "gpt-4o-mini"
    
    def generate_response(self, question: str, context_documents: List[Dict[str, Any]]) -> str:
        """Генерирует ответ на основе вопроса и контекстных документов"""
        try:
            # Формируем контекст из документов
            context_text = self._format_context(context_documents)
            
            # Формируем промпт
            prompt = f"""Используя следующие документы:

{context_text}

Ответь на вопрос: {question}

Если в предоставленных документах нет информации для ответа на вопрос, так и скажи."""
            
            # Подготавливаем сообщения
            messages = [
                {
                    "role": "system",
                    "content": "Ты - полезный ассистент, который отвечает на вопросы на основе предоставленных документов. Отвечай кратко и по существу."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            # Отправляем запрос к OpenRouter
            response = requests.post(
                self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "max_tokens": 1000,
                    "temperature": 0.7
                },
                timeout=30
            )
            
            if response.status_code != 200:
                raise Exception(f"Ошибка API OpenRouter: {response.status_code} - {response.text}")
            
            response_data = response.json()
            
            # Извлекаем ответ
            if response_data.get("choices") and len(response_data["choices"]) > 0:
                return response_data["choices"][0]["message"]["content"]
            else:
                raise Exception("Не удалось получить ответ от модели")
                
        except Exception as e:
            raise Exception(f"Ошибка при генерации ответа: {str(e)}")
    
    def _format_context(self, documents: List[Dict[str, Any]]) -> str:
        """Форматирует контекстные документы для промпта"""
        if not documents:
            return "Нет доступных документов для ответа."
        
        context_parts = []
        for i, doc in enumerate(documents, 1):
            content = doc.get('document', '')
            metadata = doc.get('metadata', {})
            file_id = metadata.get('file_id', 'Неизвестный файл')
            
            context_parts.append(f"Документ {i} (из файла: {file_id}):\n{content}\n")
        
        return "\n".join(context_parts) 