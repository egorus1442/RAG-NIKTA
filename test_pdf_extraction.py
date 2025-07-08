#!/usr/bin/env python3
"""
Тестирование извлечения текста из PDF
"""

import fitz  # PyMuPDF
import os

def test_pdf_extraction(pdf_path: str):
    """Тестирует извлечение текста из PDF"""
    try:
        print(f"📄 Открываем PDF: {pdf_path}")
        
        # Открываем PDF
        doc = fitz.open(pdf_path)
        print(f"✅ PDF открыт. Количество страниц: {len(doc)}")
        
        # Извлекаем текст с первых 3 страниц
        text = ""
        for page_num in range(min(3, len(doc))):
            page = doc[page_num]
            page_text = page.get_text()
            text += f"\n--- Страница {page_num + 1} ---\n{page_text}\n"
        
        doc.close()
        
        print(f"📝 Извлечено символов: {len(text)}")
        print(f"📄 Первые 500 символов текста:")
        print("-" * 50)
        print(text[:500])
        print("-" * 50)
        
        # Проверяем, есть ли текст
        if len(text.strip()) > 0:
            print("✅ Текст успешно извлечен!")
            return text
        else:
            print("❌ Текст не извлечен (возможно, PDF содержит только изображения)")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка при извлечении текста: {e}")
        return None

if __name__ == "__main__":
    pdf_path = "./ukrainian_cuisine.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ Файл не найден: {pdf_path}")
    else:
        test_pdf_extraction(pdf_path) 