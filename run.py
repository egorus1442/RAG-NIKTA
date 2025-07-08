#!/usr/bin/env python3
"""
Скрипт для запуска RAG API
"""

import uvicorn
import os
from dotenv import load_dotenv

def main():
    """Запуск RAG API"""
    # Загружаем переменные окружения
    load_dotenv()
    
    # Проверяем наличие необходимых переменных
    required_vars = ["OPENAI_API_KEY", "OPENROUTER_API_KEY", "API_TOKEN"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("❌ Отсутствуют необходимые переменные окружения:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nСоздайте файл .env на основе example.env и заполните все переменные.")
        return
    
    print("🚀 Запуск RAG API...")
    print("📖 Документация: http://localhost:8000/docs")
    print("🔍 OpenAPI схема: http://localhost:8000/openapi.json")
    print("💚 Health check: http://localhost:8000/health")
    print("\nДля остановки нажмите Ctrl+C")
    print("-" * 50)
    
    # Запускаем сервер
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main() 