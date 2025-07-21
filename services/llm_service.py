import requests
import json
from typing import List, Dict, Any
from config import Config

class LLMService:
    def __init__(self):
        self.api_key = Config.OPENROUTER_API_KEY
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "gpt-4o-mini"
    
    def generate_response(self, question: str, context_documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Генерирует ответ на основе вопроса и контекстных документов"""
        try:
            # Проверяем наличие API ключа
            if not self.api_key or not self.api_key.strip():
                raise Exception("OPENROUTER_API_KEY не установлен. Задайте ключ через эндпоинт /set-openrouter-key.")
            
            # Формируем контекст из документов (ограничиваем размер)
            context_text = self._format_context(context_documents)
            
            # Формируем промпт
            prompt = f"""Используя следующие документы:

{context_text}

Ответь на вопрос: {question}

Требования к ответу:
- Отвечай кратко и по существу (не более 2-3 предложений)
- Используй только информацию из предоставленных документов
- Если в документах нет информации для ответа, так и скажи
- Не добавляй лишних пояснений"""
            
            # Подготавливаем сообщения
            messages = [
                {
                    "role": "system",
                    "content": "Ты - полезный ассистент, который отвечает на вопросы на основе предоставленных документов. Отвечай кратко и по существу, используя только информацию из документов."
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
                    "max_tokens": 500,  # Уменьшаем максимальное количество токенов
                    "temperature": 0.3   # Уменьшаем креативность для более точных ответов
                },
                timeout=30
            )
            
            if response.status_code != 200:
                raise Exception(f"Ошибка API OpenRouter: {response.status_code} - {response.text}")
            
            response_data = response.json()
            
            # Извлекаем ответ и информацию о токенах
            if response_data.get("choices") and len(response_data["choices"]) > 0:
                answer = response_data["choices"][0]["message"]["content"]
                
                # Получаем информацию о токенах
                usage = response_data.get("usage", {})
                prompt_tokens = usage.get("prompt_tokens", 0)
                completion_tokens = usage.get("completion_tokens", 0)
                total_tokens = usage.get("total_tokens", 0)
                
                return {
                    "answer": answer,
                    "tokens": {
                        "prompt_tokens": prompt_tokens,
                        "completion_tokens": completion_tokens,
                        "total_tokens": total_tokens
                    }
                }
            else:
                raise Exception("Не удалось получить ответ от модели")
                
        except Exception as e:
            raise Exception(f"Ошибка при генерации ответа: {str(e)}")
    
    def _format_context(self, documents: List[Dict[str, Any]]) -> str:
        """Форматирует контекстные документы для промпта (с ограничением размера)"""
        if not documents:
            return "Нет доступных документов для ответа."
        
        context_parts = []
        total_length = 0
        max_context_length = 3000  # Ограничиваем общий размер контекста
        
        for i, doc in enumerate(documents, 1):
            content = doc.get('document', '')
            metadata = doc.get('metadata', {})
            filename = metadata.get('filename', 'Неизвестный файл')
            
            # Ограничиваем размер каждого документа
            if len(content) > 800:
                content = content[:800] + "..."
            
            # Проверяем общий размер контекста
            current_part = f"Документ {i} ({filename}):\n{content}\n"
            if total_length + len(current_part) > max_context_length:
                break
                
            context_parts.append(current_part)
            total_length += len(current_part)
        
        return "\n".join(context_parts) 