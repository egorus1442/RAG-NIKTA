#!/usr/bin/env python3
"""
Тестовый скрипт для проверки эндпоинтов управления OPENROUTER_API_KEY
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

def test_openrouter_key_endpoints():
    """Тестирует эндпоинты управления OPENROUTER_API_KEY"""
    
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    print("🧪 Тестирование эндпоинтов управления OPENROUTER_API_KEY")
    print("=" * 60)
    
    # 1. Проверяем текущий статус API ключа
    print("\n1. Проверка текущего статуса API ключа...")
    try:
        response = requests.get(f"{BASE_URL}/openrouter-key-status", headers=headers)
        print(f"   Статус: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Ответ: {data}")
        else:
            print(f"   Ошибка: {response.text}")
    except Exception as e:
        print(f"   Ошибка запроса: {e}")
    
    # 2. Устанавливаем тестовый API ключ
    print("\n2. Установка тестового API ключа...")
    test_api_key = "sk-or-v1-test-key-12345"
    try:
        payload = {"api_key": test_api_key}
        response = requests.post(f"{BASE_URL}/set-openrouter-key", headers=headers, json=payload)
        print(f"   Статус: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Ответ: {data}")
        else:
            print(f"   Ошибка: {response.text}")
    except Exception as e:
        print(f"   Ошибка запроса: {e}")
    
    # 3. Проверяем статус после установки
    print("\n3. Проверка статуса после установки...")
    try:
        response = requests.get(f"{BASE_URL}/openrouter-key-status", headers=headers)
        print(f"   Статус: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Ответ: {data}")
        else:
            print(f"   Ошибка: {response.text}")
    except Exception as e:
        print(f"   Ошибка запроса: {e}")
    
    # 4. Тестируем валидацию пустого ключа
    print("\n4. Тестирование валидации пустого ключа...")
    try:
        payload = {"api_key": ""}
        response = requests.post(f"{BASE_URL}/set-openrouter-key", headers=headers, json=payload)
        print(f"   Статус: {response.status_code}")
        if response.status_code == 400:
            data = response.json()
            print(f"   Ожидаемая ошибка: {data}")
        else:
            print(f"   Неожиданный ответ: {response.text}")
    except Exception as e:
        print(f"   Ошибка запроса: {e}")
    
    # 5. Тестируем без аутентификации
    print("\n5. Тестирование без аутентификации...")
    try:
        payload = {"api_key": "test-key"}
        response = requests.post(f"{BASE_URL}/set-openrouter-key", json=payload)
        print(f"   Статус: {response.status_code}")
        if response.status_code == 401:
            print("   Ожидаемая ошибка аутентификации")
        else:
            print(f"   Неожиданный ответ: {response.text}")
    except Exception as e:
        print(f"   Ошибка запроса: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Тестирование завершено!")

if __name__ == "__main__":
    test_openrouter_key_endpoints() 