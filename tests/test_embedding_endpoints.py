#!/usr/bin/env python3
"""
Тестовый скрипт для проверки эндпоинтов управления типом эмбедингов
"""

import requests
import json
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Конфигурация
BASE_URL = "http://localhost:8000"
API_TOKEN = os.getenv("API_TOKEN", "rag_api_secret_token_2024")

def test_embedding_endpoints():
    """Тестирует эндпоинты управления типом эмбедингов"""
    
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    print("🧪 Тестирование эндпоинтов управления типом эмбедингов")
    print("=" * 70)
    
    # 1. Проверяем текущий статус типа эмбедингов
    print("\n1. Проверка текущего статуса типа эмбедингов...")
    try:
        response = requests.get(f"{BASE_URL}/embedding-type-status", headers=headers)
        print(f"   Статус: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Ответ: {data}")
        else:
            print(f"   Ошибка: {response.text}")
    except Exception as e:
        print(f"   Ошибка запроса: {e}")
    
    # 2. Переключаемся на локальные эмбединги
    print("\n2. Переключение на локальные эмбединги...")
    try:
        payload = {"embedding_type": "local"}
        response = requests.post(f"{BASE_URL}/set-embedding-type", headers=headers, json=payload)
        print(f"   Статус: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Ответ: {data}")
        else:
            print(f"   Ошибка: {response.text}")
    except Exception as e:
        print(f"   Ошибка запроса: {e}")
    
    # 3. Проверяем статус после переключения
    print("\n3. Проверка статуса после переключения...")
    try:
        response = requests.get(f"{BASE_URL}/embedding-type-status", headers=headers)
        print(f"   Статус: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Ответ: {data}")
        else:
            print(f"   Ошибка: {response.text}")
    except Exception as e:
        print(f"   Ошибка запроса: {e}")
    
    # 4. Переключаемся обратно на OpenAI
    print("\n4. Переключение обратно на OpenAI...")
    try:
        payload = {"embedding_type": "openai"}
        response = requests.post(f"{BASE_URL}/set-embedding-type", headers=headers, json=payload)
        print(f"   Статус: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Ответ: {data}")
        else:
            print(f"   Ошибка: {response.text}")
    except Exception as e:
        print(f"   Ошибка запроса: {e}")
    
    # 5. Тестируем неподдерживаемый тип
    print("\n5. Тестирование неподдерживаемого типа...")
    try:
        payload = {"embedding_type": "unsupported"}
        response = requests.post(f"{BASE_URL}/set-embedding-type", headers=headers, json=payload)
        print(f"   Статус: {response.status_code}")
        if response.status_code == 400:
            data = response.json()
            print(f"   Ожидаемая ошибка: {data}")
        else:
            print(f"   Неожиданный ответ: {response.text}")
    except Exception as e:
        print(f"   Ошибка запроса: {e}")
    
    # 6. Тестируем без аутентификации
    print("\n6. Тестирование без аутентификации...")
    try:
        payload = {"embedding_type": "local"}
        response = requests.post(f"{BASE_URL}/set-embedding-type", json=payload)
        print(f"   Статус: {response.status_code}")
        if response.status_code == 403:
            print("   Ожидаемая ошибка аутентификации")
        else:
            print(f"   Неожиданный ответ: {response.text}")
    except Exception as e:
        print(f"   Ошибка запроса: {e}")
    
    print("\n" + "=" * 70)
    print("✅ Тестирование завершено!")

if __name__ == "__main__":
    test_embedding_endpoints() 