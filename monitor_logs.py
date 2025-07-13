"""
Скрипт для мониторинга логов RAG API в реальном времени
"""

import time
import os
import sys
from datetime import datetime

def monitor_logs():
    """Мониторит лог файл в реальном времени"""
    
    log_file = "rag_api.log"
    
    if not os.path.exists(log_file):
        print(f"❌ Лог файл не найден: {log_file}")
        print("💡 Запустите API для создания лог файла")
        return
    
    print("🔍 Мониторинг логов RAG API в реальном времени")
    print("=" * 60)
    print("💡 Нажмите Ctrl+C для остановки")
    print()
    
    # Читаем текущий размер файла
    with open(log_file, 'r', encoding='utf-8') as f:
        f.seek(0, 2)  # Переходим в конец файла
        last_position = f.tell()
    
    try:
        while True:
            with open(log_file, 'r', encoding='utf-8') as f:
                f.seek(last_position)
                new_lines = f.readlines()
                last_position = f.tell()
            
            for line in new_lines:
                line = line.strip()
                if line:
                    # Определяем тип записи и добавляем эмодзи
                    if "ФАЙЛ ОБРАБОТАН" in line:
                        if "Обработан LLM: ДА" in line:
                            print(f"🤖 {line}")
                        else:
                            print(f"📖 {line}")
                    elif "ЗАПРОС ПОЛУЧЕН" in line:
                        print(f"❓ {line}")
                    elif "НАЙДЕНЫ ДОКУМЕНТЫ" in line:
                        print(f"📚 {line}")
                    elif "ОТВЕТ СГЕНЕРИРОВАН" in line:
                        print(f"💬 {line}")
                    elif "УДАЛЕНИЕ ФАЙЛА" in line:
                        print(f"🗑️ {line}")
                    elif "ОШИБКА" in line:
                        print(f"❌ {line}")
                    elif "ПРЕДУПРЕЖДЕНИЕ" in line or "WARNING" in line:
                        print(f"⚠️ {line}")
                    else:
                        print(f"ℹ️ {line}")
            
            time.sleep(1)  # Проверяем каждую секунду
            
    except KeyboardInterrupt:
        print("\n👋 Мониторинг остановлен")

def show_statistics():
    """Показывает краткую статистику"""
    
    log_file = "rag_api.log"
    
    if not os.path.exists(log_file):
        return
    
    with open(log_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Подсчитываем статистику
    file_processed = len([l for l in lines if "ФАЙЛ ОБРАБОТАН" in l])
    llm_processed = len([l for l in lines if "Обработан LLM: ДА" in l])
    queries = len([l for l in lines if "ЗАПРОС ПОЛУЧЕН" in l])
    errors = len([l for l in lines if "ОШИБКА" in l])
    
    print(f"📊 Статистика: Файлов: {file_processed}, LLM: {llm_processed}, Запросов: {queries}, Ошибок: {errors}")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--stats":
        show_statistics()
    else:
        monitor_logs()

if __name__ == "__main__":
    main() 