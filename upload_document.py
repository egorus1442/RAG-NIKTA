"""
Скрипт для загрузки документов в RAG API
"""

import requests
import os
import sys

def upload_document(file_path: str, api_token: str = "rag_api_secret_token_2024"):
    """Загружает документ в RAG API"""
    
    if not os.path.exists(file_path):
        print(f"❌ Файл не найден: {file_path}")
        return None
    
    url = "http://localhost:8000/upload"
    headers = {"Authorization": f"Bearer {api_token}"}
    
    try:
        with open(file_path, "rb") as f:
            files = {"file": f}
            response = requests.post(url, headers=headers, files=files)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Файл успешно загружен!")
            print(f"📄 ID файла: {result['file_id']}")
            print(f"📝 Имя файла: {result['filename']}")
            print(f"🔢 Количество чанков: {result['chunks_count']}")
            print(f"💬 Сообщение: {result['message']}")
            return result['file_id']
        else:
            print(f"❌ Ошибка загрузки: {response.status_code}")
            print(f"📄 Ответ: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

def query_document(question: str, api_token: str = "rag_api_secret_token_2024"):
    """Задает вопрос к загруженным документам"""
    
    url = "http://localhost:8000/query"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    data = {"question": question}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n🤖 Ответ на вопрос: '{question}'")
            print(f"📝 {result['answer']}")
            print(f"📚 Найдено документов: {len(result['context_documents'])}")
            return result
        else:
            print(f"❌ Ошибка запроса: {response.status_code}")
            print(f"📄 Ответ: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

def main():
    """Основная функция"""
    print("📚 Загрузка документа в RAG API")
    print("=" * 40)
    
    # Проверяем аргументы командной строки
    if len(sys.argv) < 2:
        print("Использование: python3 upload_document.py <путь_к_файлу>")
        print("Пример: python3 upload_document.py document.pdf")
        return
    
    file_path = sys.argv[1]
    
    # Загружаем документ
    file_id = upload_document(file_path)
    
    if file_id:
        print(f"\n🎉 Документ загружен! ID: {file_id}")
        
        # Интерактивный режим для вопросов
        print("\n💬 Теперь можете задавать вопросы (нажмите Ctrl+C для выхода):")
        
        try:
            while True:
                question = input("\n❓ Ваш вопрос: ")
                if question.lower() in ['exit', 'quit', 'выход']:
                    break
                query_document(question)
        except KeyboardInterrupt:
            print("\n👋 До свидания!")
    else:
        print("❌ Не удалось загрузить документ")

if __name__ == "__main__":
    main() 