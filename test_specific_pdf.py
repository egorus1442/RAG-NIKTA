#!/usr/bin/env python3
"""
Тестовый скрипт для конкретного PDF файла
"""

import os
import sys
from services.ai_pdf_converter import AIPDFConverter
from utils.text_extractor import TextExtractor

def test_specific_pdf():
    """Тестирует обработку конкретного PDF файла"""
    print("🧪 Тестирование конкретного PDF файла")
    print("=" * 60)
    
    # Путь к тестовому файлу
    pdf_path = "/Users/apple/Desktop/Kira/RAG/Доклад_78a1afbd.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ Файл не найден: {pdf_path}")
        return
    
    print(f"📄 Тестируемый файл: {pdf_path}")
    print(f"📊 Размер файла: {os.path.getsize(pdf_path)} байт")
    print()
    
    # Тест 1: Проверка стандартной конвертации
    print("1️⃣ Тест стандартной конвертации (PyMuPDF):")
    try:
        text_data = TextExtractor.extract_text_with_metadata(pdf_path)
        text = text_data['text']
        metadata = text_data['metadata']
        
        print(f"   ✅ Конвертация успешна")
        print(f"   📄 Длина текста: {len(text)} символов")
        print(f"   📖 Количество слов: {metadata.get('total_words', 0)}")
        print(f"   📊 Количество страниц: {metadata.get('total_pages', 0)}")
        print(f"   🔍 Первые 200 символов:")
        print(f"   {'-' * 50}")
        print(f"   {text[:200]}...")
        print(f"   {'-' * 50}")
        
        # Проверяем, есть ли текстовый слой
        if len(text.strip()) < 50:
            print(f"   ⚠️ Текста мало - возможно отсканированный PDF")
            needs_ai = True
        else:
            print(f"   ✅ Текстовый слой присутствует")
            needs_ai = False
            
    except Exception as e:
        print(f"   ❌ Ошибка стандартной конвертации: {e}")
        needs_ai = True
    
    print()
    
    # Тест 2: Проверка определения отсканированного PDF
    print("2️⃣ Тест определения отсканированного PDF:")
    try:
        converter = AIPDFConverter()
        is_scanned = converter.is_pdf_scanned(pdf_path)
        print(f"   🔍 Отсканированный PDF: {is_scanned}")
        
        if is_scanned:
            print(f"   💡 Рекомендуется ИИ-конвертация")
        else:
            print(f"   💡 Стандартная конвертация достаточна")
            
    except Exception as e:
        print(f"   ❌ Ошибка при проверке: {e}")
    
    print()
    
    # Тест 3: ИИ-конвертация (если нужно)
    if needs_ai or is_scanned:
        print("3️⃣ Тест ИИ-конвертации:")
        try:
            ai_result = converter.extract_text_with_ai_fallback(pdf_path)
            ai_text = ai_result['text']
            ai_metadata = ai_result['metadata']
            
            print(f"   ✅ ИИ-конвертация успешна")
            print(f"   📄 Длина текста: {len(ai_text)} символов")
            print(f"   📖 Количество слов: {ai_metadata.get('total_words', 0)}")
            print(f"   📊 Количество страниц: {ai_metadata.get('total_pages', 0)}")
            print(f"   🤖 Страниц обработано ИИ: {ai_metadata.get('ai_converted_pages', 0)}")
            print(f"   📝 Метод конвертации: {ai_metadata.get('conversion_method', 'unknown')}")
            print(f"   🔍 Первые 200 символов:")
            print(f"   {'-' * 50}")
            print(f"   {ai_text[:200]}...")
            print(f"   {'-' * 50}")
            
            # Сохраняем результат
            output_path = "test_output.txt"
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(ai_text)
            print(f"   💾 Результат сохранен в: {output_path}")
            
        except Exception as e:
            print(f"   ❌ Ошибка ИИ-конвертации: {e}")
    else:
        print("3️⃣ ИИ-конвертация не требуется")
    
    print()
    print("✅ Тестирование завершено!")

def main():
    """Основная функция"""
    test_specific_pdf()

if __name__ == "__main__":
    main() 