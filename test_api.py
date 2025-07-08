#!/usr/bin/env python3
"""
Простой тестовый скрипт для проверки работы RAG API
"""

import requests
import json
import os
from typing import Optional

class RAGAPIClient:
    def __init__(self, base_url: str = "http://localhost:8000", api_token: Optional[str] = None):
        self.base_url = base_url
        self.api_token = api_token or os.getenv("API_TOKEN")
        if not self.api_token:
            raise ValueError("API_TOKEN не установлен. Установите переменную окружения или передайте в конструктор.")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
    
    def health_check(self) -> dict:
        """Проверка состояния API"""
        response = requests.get(f"{self.base_url}/health")
        return response.json()
    
    def upload_file(self, file_path: str) -> dict:
        """Загрузка файла"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Файл не найден: {file_path}")
        
        headers = {"Authorization": f"Bearer {self.api_token}"}
        
        with open(file_path, "rb") as f:
            files = {"file": f}
            response = requests.post(
                f"{self.base_url}/upload",
                headers=headers,
                files=files
            )
        
        if response.status_code != 200:
            raise Exception(f"Ошибка загрузки: {response.status_code} - {response.text}")
        
        return response.json()
    
    def query(self, question: str) -> dict:
        """Запрос к API"""
        data = {"question": question}
        response = requests.post(
            f"{self.base_url}/query",
            headers=self.headers,
            json=data
        )
        
        if response.status_code != 200:
            raise Exception(f"Ошибка запроса: {response.status_code} - {response.text}")
        
        return response.json()
    
    def delete_file(self, file_id: str) -> dict:
        """Удаление файла"""
        response = requests.delete(
            f"{self.base_url}/file/{file_id}",
            headers=self.headers
        )
        
        if response.status_code != 200:
            raise Exception(f"Ошибка удаления: {response.status_code} - {response.text}")
        
        return response.json()

def create_test_file(content: str, filename: str = "test_document.txt") -> str:
    """Создает тестовый файл"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    return filename

def main():
    """Основная функция тестирования"""
    print("🚀 Тестирование RAG API")
    print("=" * 50)
    
    try:
        # Инициализируем клиент
        client = RAGAPIClient()
        
        # Проверяем состояние API
        print("1. Проверка состояния API...")
        health = client.health_check()
        print(f"✅ API статус: {health}")
        
        # Создаем тестовый файл
        print("\n2. Создание тестового файла...")
        test_content = """
        Искусственный интеллект (ИИ) - это область компьютерных наук, 
        которая занимается созданием систем, способных выполнять задачи, 
        которые обычно требуют человеческого интеллекта. 
        
        Машинное обучение является подразделом ИИ и включает в себя 
        алгоритмы, которые позволяют компьютерам учиться на основе данных 
        без явного программирования.
        
        Глубокое обучение - это подраздел машинного обучения, 
        использующий нейронные сети с множественными слоями для 
        обработки сложных паттернов в данных.
        """
        
        test_file = create_test_file(test_content)
        print(f"✅ Создан тестовый файл: {test_file}")
        
        # Загружаем файл
        print("\n3. Загрузка файла...")
        upload_result = client.upload_file(test_file)
        file_id = upload_result["file_id"]
        print(f"✅ Файл загружен: {upload_result}")
        
        # Тестируем запросы
        print("\n4. Тестирование запросов...")
        
        questions = [
            "Что такое искусственный интеллект?",
            "Как связаны машинное обучение и ИИ?",
            "Что такое глубокое обучение?",
            "Какие технологии используются в ИИ?"
        ]
        
        for i, question in enumerate(questions, 1):
            print(f"\n   Вопрос {i}: {question}")
            try:
                result = client.query(question)
                print(f"   Ответ: {result['answer'][:100]}...")
                print(f"   Найдено документов: {len(result['context_documents'])}")
            except Exception as e:
                print(f"   ❌ Ошибка: {e}")
        
        # Удаляем файл
        print(f"\n5. Удаление файла {file_id}...")
        delete_result = client.delete_file(file_id)
        print(f"✅ Файл удален: {delete_result}")
        
        # Удаляем тестовый файл
        os.remove(test_file)
        print(f"✅ Тестовый файл удален: {test_file}")
        
        print("\n🎉 Все тесты прошли успешно!")
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        print("\nУбедитесь, что:")
        print("1. API запущено (python main.py)")
        print("2. Установлены все зависимости (pip install -r requirements.txt)")
        print("3. Настроены переменные окружения (.env файл)")
        print("4. API_TOKEN установлен в переменных окружения")

if __name__ == "__main__":
    main() 