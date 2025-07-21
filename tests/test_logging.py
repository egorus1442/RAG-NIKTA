"""
Тестовый скрипт для проверки системы логирования
"""

import requests
import time
import os

def test_logging():
    """Тестирует систему логирования"""
    
    print("🧪 Тестирование системы логирования")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    api_token = "rag_api_secret_token_2024"
    headers = {
        "Authorization": f"Bearer {api_token}"
    }
    
    # Проверяем, запущен ли сервер
    try:
        health_response = requests.get(f"{base_url}/health")
        if health_response.status_code != 200:
            print("❌ Сервер не отвечает")
            return
        print("✅ Сервер запущен")
    except requests.exceptions.ConnectionError:
        print("❌ Не удается подключиться к серверу")
        print("💡 Запустите сервер: python main.py")
        return
    
    # Тест 1: Загрузка файла
    print("\n1️⃣ Тест загрузки файла:")
    
    # Создаем тестовый файл
    test_content = "Это тестовый документ для проверки логирования."
    with open("test_logging.txt", "w", encoding="utf-8") as f:
        f.write(test_content)
    
    try:
        with open("test_logging.txt", "rb") as f:
            files = {"file": f}
            upload_response = requests.post(
                f"{base_url}/upload",
                headers=headers,
                files=files
            )
        
        if upload_response.status_code == 200:
            upload_data = upload_response.json()
            file_id = upload_data["file_id"]
            print(f"   ✅ Файл загружен с ID: {file_id}")
            
            # Ждем немного для записи логов
            time.sleep(1)
            
            # Проверяем лог файл
            if os.path.exists("rag_api.log"):
                with open("rag_api.log", "r", encoding="utf-8") as f:
                    log_content = f.read()
                    if "ФАЙЛ ОБРАБОТАН" in log_content and file_id in log_content:
                        print("   ✅ Запись в лог файле найдена")
                        
                        # Проверяем, есть ли информация о LLM
                        if "Обработан LLM:" in log_content:
                            print("   ✅ Информация о LLM обработке записана")
                        else:
                            print("   ⚠️ Информация о LLM обработке не найдена")
                    else:
                        print("   ❌ Запись в лог файле не найдена")
            else:
                print("   ❌ Лог файл не создан")
        else:
            print(f"   ❌ Ошибка загрузки: {upload_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
    
    # Тест 2: Запрос к документам
    print("\n2️⃣ Тест запроса к документам:")
    
    try:
        query_data = {"question": "Что содержится в документе?"}
        query_response = requests.post(
            f"{base_url}/query",
            headers=headers,
            json=query_data
        )
        
        if query_response.status_code == 200:
            print("   ✅ Запрос выполнен успешно")
            
            # Ждем немного для записи логов
            time.sleep(1)
            
            # Проверяем лог файл
            if os.path.exists("rag_api.log"):
                with open("rag_api.log", "r", encoding="utf-8") as f:
                    log_content = f.read()
                    if "ЗАПРОС ПОЛУЧЕН" in log_content:
                        print("   ✅ Запрос записан в лог")
                    if "НАЙДЕНЫ ДОКУМЕНТЫ" in log_content:
                        print("   ✅ Информация о найденных документах записана")
                    if "ОТВЕТ СГЕНЕРИРОВАН" in log_content:
                        print("   ✅ Информация о сгенерированном ответе записана")
        else:
            print(f"   ❌ Ошибка запроса: {query_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
    
    # Тест 3: Удаление файла
    print("\n3️⃣ Тест удаления файла:")
    
    try:
        delete_response = requests.delete(
            f"{base_url}/file/{file_id}",
            headers=headers
        )
        
        if delete_response.status_code == 200:
            print("   ✅ Файл удален успешно")
            
            # Ждем немного для записи логов
            time.sleep(1)
            
            # Проверяем лог файл
            if os.path.exists("rag_api.log"):
                with open("rag_api.log", "r", encoding="utf-8") as f:
                    log_content = f.read()
                    if "УДАЛЕНИЕ ФАЙЛА" in log_content:
                        print("   ✅ Операция удаления записана в лог")
        else:
            print(f"   ❌ Ошибка удаления: {delete_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
    
    # Очистка
    if os.path.exists("test_logging.txt"):
        os.remove("test_logging.txt")
    
    print("\n✅ Тестирование завершено!")
    print("💡 Для просмотра логов используйте: python view_logs.py")
    print("💡 Для мониторинга в реальном времени: python monitor_logs.py")

if __name__ == "__main__":
    test_logging() 