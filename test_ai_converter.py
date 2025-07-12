#!/usr/bin/env python3
"""
Тестовый скрипт для проверки ИИ-конвертации PDF
"""

import os
import sys
from services.ai_pdf_converter import AIPDFConverter

def test_ai_converter():
    """Тестирует AIPDFConverter"""
    print("🤖 Тестирование ИИ-конвертации PDF")
    print("=" * 50)
    
    # Инициализируем конвертер
    converter = AIPDFConverter()
    
    # Тест 1: Проверка определения отсканированного PDF
    print("1️⃣ Тест определения отсканированного PDF:")
    
    # Создаем тестовый PDF с минимальным текстом
    test_pdf_path = "test_scanned.pdf"
    
    # Проверяем, есть ли тестовый PDF
    if os.path.exists(test_pdf_path):
        try:
            is_scanned = converter.is_pdf_scanned(test_pdf_path)
            print(f"   📄 Файл: {test_pdf_path}")
            print(f"   🔍 Отсканированный: {is_scanned}")
        except Exception as e:
            print(f"   ❌ Ошибка при проверке: {e}")
    else:
        print(f"   ⚠️ Тестовый PDF не найден: {test_pdf_path}")
        print(f"   💡 Создайте PDF файл для тестирования")
    
    print()
    
    # Тест 2: Проверка конфигурации
    print("2️⃣ Тест конфигурации:")
    print(f"   🔑 API ключ: {'✅ Установлен' if converter.api_key else '❌ Не установлен'}")
    print(f"   🤖 Модель: {converter.model}")
    print(f"   📁 Poppler путь: {converter.poppler_path or 'По умолчанию'}")
    
    print()
    
    # Тест 3: Проверка кодирования изображений
    print("3️⃣ Тест кодирования изображений:")
    try:
        from PIL import Image
        import io
        
        # Создаем тестовое изображение
        test_image = Image.new('RGB', (100, 100), color='white')
        
        # Кодируем в base64
        b64_data = converter.encode_image_to_base64(test_image)
        
        print(f"   ✅ Изображение закодировано успешно")
        print(f"   📊 Размер base64: {len(b64_data)} символов")
        print(f"   🔍 Начинается с: {b64_data[:20]}...")
        
    except Exception as e:
        print(f"   ❌ Ошибка при кодировании: {e}")
    
    print()
    
    # Тест 4: Проверка доступности зависимостей
    print("4️⃣ Тест зависимостей:")
    
    dependencies = [
        ("PyPDF2", "PyPDF2"),
        ("pdf2image", "pdf2image"),
        ("PIL", "PIL"),
        ("requests", "requests")
    ]
    
    for name, module in dependencies:
        try:
            __import__(module)
            print(f"   ✅ {name}: Установлен")
        except ImportError:
            print(f"   ❌ {name}: Не установлен")
    
    print()
    print("✅ Тестирование ИИ-конвертации завершено!")
    print()
    print("💡 Для полного тестирования:")
    print("   1. Установите зависимости: pip install PyPDF2 pdf2image Pillow requests")
    print("   2. Создайте тестовый PDF файл")
    print("   3. Убедитесь, что OPENROUTER_API_KEY установлен в .env")

def main():
    """Основная функция"""
    test_ai_converter()

if __name__ == "__main__":
    main() 