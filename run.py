#!/usr/bin/env python3
"""
Скрипт для запуска RAG API
"""

import uvicorn
import os
import subprocess
import sys
from dotenv import load_dotenv

def check_port_usage():
    """Проверяет, занят ли порт 8000"""
    try:
        result = subprocess.run("lsof -i :8000", shell=True, capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            print("⚠️  Порт 8000 занят!")
            print("   Найденные процессы:")
            for line in result.stdout.strip().split('\n')[1:]:  # Пропускаем заголовок
                if line.strip():
                    print(f"   {line.strip()}")
            return True
        return False
    except Exception:
        return False

def check_dependencies():
    """Проверяет критические зависимости"""
    try:
        import numpy
        if numpy.__version__.startswith('2.'):
            print("❌ Обнаружена несовместимая версия NumPy 2.x")
            print("   ChromaDB не совместим с NumPy 2.0+")
            print("   Запустите: python3 fix_dependencies.py")
            return False
        
        import six
        import dateutil
        return True
    except ImportError as e:
        print(f"❌ Отсутствует зависимость: {e}")
        print("   Запустите: python3 fix_dependencies.py")
        return False

def main():
    """Запуск RAG API"""
    print("🔍 Проверка системы...")
    
    # Проверяем зависимости
    if not check_dependencies():
        return
    
    # Проверяем порт
    if check_port_usage():
        print("\n❌ Порт 8000 занят. Освободите порт или измените порт в настройках.")
        print("   Команды для освобождения порта:")
        print("   - lsof -i :8000  # найти процесс")
        print("   - kill -9 <PID>  # остановить процесс")
        return
    
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
    
    print("✅ Все проверки пройдены!")
    print("\n🚀 Запуск RAG API...")
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