"""
Тестовый скрипт для проверки FileProcessor сервиса
"""

import os
import sys
from services.file_processor import FileProcessor

def test_file_processor():
    """Тестирует FileProcessor"""
    print("🧪 Тестирование FileProcessor")
    print("=" * 50)
    
    # Инициализируем FileProcessor
    upload_dir = "uploads"
    processor = FileProcessor(upload_dir)
    
    # Тест 1: Обработка текстового файла
    print("1️⃣ Тест обработки текстового файла:")
    test_content = "Это тестовый текст для проверки FileProcessor.\nВторая строка текста.\nТретья строка.".encode('utf-8')
    test_filename = "test_document.txt"
    
    try:
        result = processor.process_uploaded_file(test_content, test_filename)
        print(f"   ✅ Файл обработан успешно")
        print(f"   📄 File ID: {result['file_id']}")
        print(f"   📁 Оригинал: {result['original_path']}")
        print(f"   📝 TXT версия: {result['txt_path']}")
        print(f"   📊 Размер: {result['file_size']} байт")
        print(f"   📖 Тип файла: {result['file_type']}")
        print(f"   📄 Длина текста: {len(result['text'])} символов")
        
        # Проверяем, что файлы созданы
        if os.path.exists(result['original_path']):
            print(f"   ✅ Оригинал создан")
        else:
            print(f"   ❌ Оригинал не создан")
            
        if os.path.exists(result['txt_path']):
            print(f"   ✅ TXT версия создана")
        else:
            print(f"   ❌ TXT версия не создана")
        
        file_id = result['file_id']
        
    except Exception as e:
        print(f"   ❌ Ошибка при обработке: {e}")
        return
    
    print()
    
    # Тест 2: Получение информации о файле
    print("2️⃣ Тест получения информации о файле:")
    try:
        file_info = processor.get_file_info(file_id)
        print(f"   📄 File ID: {file_info['file_id']}")
        print(f"   📁 Существует: {file_info['exists']}")
        print(f"   📁 Оригинал: {file_info['original_path']}")
        print(f"   📝 TXT версия: {file_info['txt_path']}")
    except Exception as e:
        print(f"   ❌ Ошибка при получении информации: {e}")
    
    print()
    
    # Тест 3: Удаление файла
    print("3️⃣ Тест удаления файла:")
    try:
        deleted = processor.delete_file_versions(file_id)
        if deleted:
            print(f"   ✅ Файлы удалены успешно")
            
            # Проверяем, что файлы действительно удалены
            file_info = processor.get_file_info(file_id)
            if not file_info['exists']:
                print(f"   ✅ Файлы действительно удалены с диска")
            else:
                print(f"   ❌ Файлы все еще существуют на диске")
        else:
            print(f"   ❌ Файлы не найдены для удаления")
    except Exception as e:
        print(f"   ❌ Ошибка при удалении: {e}")
    
    print()
    
    # Тест 4: Обработка неподдерживаемого формата
    print("4️⃣ Тест обработки неподдерживаемого формата:")
    try:
        result = processor.process_uploaded_file(b"test content", "test.xyz")
        print(f"   ❌ Неожиданный успех для неподдерживаемого формата")
    except ValueError as e:
        print(f"   ✅ Правильно обработана ошибка: {e}")
    except Exception as e:
        print(f"   ❌ Неожиданная ошибка: {e}")
    
    print()
    print("✅ Тестирование FileProcessor завершено!")

def main():
    """Основная функция"""
    if not os.path.exists("uploads"):
        print("❌ Папка uploads не найдена!")
        return
    
    test_file_processor()

if __name__ == "__main__":
    main() 