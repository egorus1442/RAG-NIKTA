#!/usr/bin/env python3
"""
Тестовый скрипт для проверки новой логики извлечения PDF
"""

import os
import sys
from utils.text_extractor import TextExtractor

def test_pdf_extraction(file_path: str):
    """Тестирует различные методы извлечения PDF"""
    print(f"🔍 Тестирование извлечения PDF: {file_path}")
    print("=" * 60)
    
    if not os.path.exists(file_path):
        print(f"❌ Файл не найден: {file_path}")
        return
    
    try:
        # 1. Обычное извлечение
        print("1️⃣ Обычное извлечение текста:")
        text = TextExtractor.extract_text(file_path)
        print(f"   Длина текста: {len(text)} символов")
        print(f"   Количество слов: {len(text.split())}")
        print(f"   Первые 200 символов: {text[:200]}...")
        print()
        
        # 2. Извлечение с метаданными
        print("2️⃣ Извлечение с метаданными:")
        text_data = TextExtractor.extract_text_with_metadata(file_path)
        metadata = text_data['metadata']
        print(f"   Всего страниц: {metadata.get('total_pages', 0)}")
        print(f"   Всего таблиц: {metadata.get('total_tables', 0)}")
        print(f"   Всего слов: {metadata.get('total_words', 0)}")
        print(f"   Всего символов: {metadata.get('total_chars', 0)}")
        print()
        
        # 3. Структурированное извлечение
        print("3️⃣ Структурированное извлечение:")
        structured_text = TextExtractor._extract_from_pdf_structured(file_path)
        print(f"   Длина структурированного текста: {len(structured_text)} символов")
        print(f"   Первые 300 символов:")
        print(f"   {structured_text[:300]}...")
        print()
        
        # 4. Разбивка на чанки
        print("4️⃣ Разбивка на чанки:")
        
        # Обычная разбивка
        chunks_normal = TextExtractor.chunk_text(text, chunk_size=1000, overlap=200)
        print(f"   Обычная разбивка: {len(chunks_normal)} чанков")
        
        # Разбивка по страницам
        chunks_pages = TextExtractor.chunk_by_pages(structured_text)
        print(f"   Разбивка по страницам: {len(chunks_pages)} чанков")
        
        # Разбивка по абзацам
        chunks_paragraphs = TextExtractor.chunk_by_paragraphs(text, max_chunk_size=1000)
        print(f"   Разбивка по абзацам: {len(chunks_paragraphs)} чанков")
        print()
        
        # 5. Примеры чанков
        print("5️⃣ Примеры чанков:")
        if chunks_pages:
            print(f"   Первый чанк (страница):")
            print(f"   {chunks_pages[0][:200]}...")
            print()
        
        if chunks_paragraphs:
            print(f"   Первый чанк (абзац):")
            print(f"   {chunks_paragraphs[0][:200]}...")
            print()
        
        print("✅ Тестирование завершено успешно!")
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Основная функция"""
    print("🧪 Тестирование новой логики извлечения PDF")
    print("=" * 60)
    
    # Проверяем аргументы командной строки
    if len(sys.argv) < 2:
        print("Использование: python3 test_pdf_extraction.py <путь_к_pdf_файлу>")
        print("Пример: python3 test_pdf_extraction.py uploads/document.pdf")
        
        # Пытаемся найти PDF файлы в папке uploads
        uploads_dir = "uploads"
        if os.path.exists(uploads_dir):
            pdf_files = [f for f in os.listdir(uploads_dir) if f.lower().endswith('.pdf')]
            if pdf_files:
                print(f"\nНайдены PDF файлы в папке {uploads_dir}:")
                for i, pdf_file in enumerate(pdf_files, 1):
                    print(f"   {i}. {pdf_file}")
                print(f"\nЗапустите: python3 test_pdf_extraction.py uploads/{pdf_files[0]}")
        return
    
    file_path = sys.argv[1]
    test_pdf_extraction(file_path)

if __name__ == "__main__":
    main() 