"""
Скрипт для просмотра логов обработки файлов
"""

import os
import re
from datetime import datetime

def view_file_processing_logs():
    """Показывает логи обработки файлов"""
    
    log_file = "rag_api.log"
    
    if not os.path.exists(log_file):
        print(f"❌ Лог файл не найден: {log_file}")
        print("💡 Запустите API и загрузите несколько файлов для создания логов")
        return
    
    print("📋 Логи обработки файлов RAG API")
    print("=" * 60)
    
    # Читаем лог файл
    with open(log_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Фильтруем строки с обработкой файлов
    file_processing_lines = []
    query_lines = []
    
    for line in lines:
        if "ФАЙЛ ОБРАБОТАН" in line:
            file_processing_lines.append(line.strip())
        elif "ЗАПРОС ПОЛУЧЕН" in line or "НАЙДЕНЫ ДОКУМЕНТЫ" in line:
            query_lines.append(line.strip())
    
    # Показываем статистику обработки файлов
    print(f"📊 Всего записей в логе: {len(lines)}")
    print(f"📁 Обработанных файлов: {len(file_processing_lines)}")
    print(f"❓ Запросов: {len([l for l in query_lines if 'ЗАПРОС ПОЛУЧЕН' in l])}")
    print()
    
    # Показываем последние 10 обработанных файлов
    if file_processing_lines:
        print("🔄 Последние обработанные файлы:")
        print("-" * 60)
        
        for line in file_processing_lines[-10:]:
            # Извлекаем ключевую информацию
            match = re.search(r'ФАЙЛ ОБРАБОТАН - ID: ([^,]+), Имя: ([^,]+), Тип: ([^,]+), Размер: ([^,]+), Метод конвертации: ([^,]+), Обработан LLM: ([^,]+)', line)
            if match:
                file_id, filename, file_type, size, method, llm_processed = match.groups()
                timestamp = line.split(' - ')[0]
                
                # Определяем эмодзи для типа файла
                file_emoji = "📄" if file_type == ".pdf" else "📝" if file_type == ".txt" else "📘" if file_type == ".docx" else "📁"
                
                # Определяем эмодзи для LLM обработки
                llm_emoji = "🤖" if llm_processed == "ДА" else "📖"
                
                print(f"{timestamp} {file_emoji} {filename} {llm_emoji} {method}")
                print(f"   ID: {file_id[:8]}... | Размер: {size} | LLM: {llm_processed}")
                print()
    else:
        print("📭 Нет записей об обработанных файлах")
    
    # Показываем статистику по методам обработки
    if file_processing_lines:
        print("📈 Статистика по методам обработки:")
        print("-" * 40)
        
        methods = {}
        llm_count = 0
        standard_count = 0
        
        for line in file_processing_lines:
            if "Обработан LLM: ДА" in line:
                llm_count += 1
            elif "Обработан LLM: НЕТ" in line:
                standard_count += 1
            
            # Подсчитываем методы конвертации
            match = re.search(r'Метод конвертации: ([^,]+)', line)
            if match:
                method = match.group(1)
                methods[method] = methods.get(method, 0) + 1
        
        print(f"🤖 Обработано LLM: {llm_count}")
        print(f"📖 Стандартная обработка: {standard_count}")
        print()
        
        print("🔧 Методы конвертации:")
        for method, count in methods.items():
            print(f"   {method}: {count}")
    
    print()
    print("💡 Для просмотра полного лога используйте: tail -f rag_api.log")

def view_recent_queries():
    """Показывает последние запросы"""
    
    log_file = "rag_api.log"
    
    if not os.path.exists(log_file):
        return
    
    with open(log_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Находим последние запросы
    recent_queries = []
    current_query = {}
    
    for line in lines:
        line = line.strip()
        if "ЗАПРОС ПОЛУЧЕН" in line:
            if current_query:
                recent_queries.append(current_query)
            current_query = {"query": line, "docs": None, "answer": None}
        elif "НАЙДЕНЫ ДОКУМЕНТЫ" in line and current_query:
            current_query["docs"] = line
        elif "ОТВЕТ СГЕНЕРИРОВАН" in line and current_query:
            current_query["answer"] = line
            recent_queries.append(current_query)
            current_query = {}
    
    if recent_queries:
        print("❓ Последние запросы:")
        print("-" * 60)
        
        for i, query_data in enumerate(recent_queries[-5:], 1):
            timestamp = query_data["query"].split(' - ')[0]
            question = query_data["query"].split('Вопрос: ')[1] if 'Вопрос: ' in query_data["query"] else "Неизвестно"
            
            print(f"{i}. {timestamp}")
            print(f"   Вопрос: {question}")
            
            if query_data["docs"]:
                docs_info = query_data["docs"].split('НАЙДЕНЫ ДОКУМЕНТЫ - ')[1] if 'НАЙДЕНЫ ДОКУМЕНТЫ - ' in query_data["docs"] else "Неизвестно"
                print(f"   Документы: {docs_info}")
            
            if query_data["answer"]:
                answer_info = query_data["answer"].split('ОТВЕТ СГЕНЕРИРОВАН - ')[1] if 'ОТВЕТ СГЕНЕРИРОВАН - ' in query_data["answer"] else "Неизвестно"
                print(f"   Ответ: {answer_info}")
            
            print()

def main():
    print("🔍 Просмотр логов RAG API")
    print("=" * 60)
    
    view_file_processing_logs()
    print()
    view_recent_queries()

if __name__ == "__main__":
    main() 