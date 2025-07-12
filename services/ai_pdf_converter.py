import os
import io
import base64
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

import requests
from PyPDF2 import PdfReader
from PyPDF2.errors import PdfReadError
from pdf2image import convert_from_path
from pdf2image.exceptions import PDFInfoNotInstalledError, PDFPageCountError
from PIL import Image

from config import Config

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s %(levelname)s [%(threadName)s]: %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class AIPDFConverter:
    """Сервис для конвертации PDF в текст с помощью ИИ"""
    
    def __init__(self, api_key: str = None, model: str = "google/gemini-2.5-flash"):
        self.api_key = api_key or Config.OPENROUTER_API_KEY
        self.model = model
        self.poppler_path = None  # Можно настроить путь к poppler
        
    def encode_image_to_base64(self, pil_image: Image.Image) -> str:
        """Кодирует PIL.Image в base64 JPEG."""
        buffer = io.BytesIO()
        pil_image.save(buffer, format="JPEG", quality=85)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")
    
    def send_page_to_llm(self, base64_image: str, instruction: str) -> str:
        """Отправляет страницу в LLM и возвращает распознанный текст."""
        data_url = f"data:image/jpeg;base64,{base64_image}"
        messages = [
            {"role": "user", "content": [
                {"type": "text", "text": instruction},
                {"type": "image_url", "image_url": {"url": data_url}}
            ]}
        ]
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": 4000
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            resp = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=120
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
        except requests.RequestException as e:
            logger.error(f"Ошибка при запросе к LLM: {e}")
            raise Exception(f"Ошибка ИИ-конвертации: {str(e)}")
    
    def extract_text_with_ai_fallback(self, pdf_path: str) -> Dict[str, Any]:
        """
        Извлекает текст из PDF с fallback на ИИ-конвертацию
        
        Args:
            pdf_path: Путь к PDF файлу
            
        Returns:
            Dict с текстом и метаданными
        """
        logger.info(f"Начинаем обработку PDF: {pdf_path}")
        
        try:
            reader = PdfReader(pdf_path)
        except (PdfReadError, FileNotFoundError) as e:
            raise Exception(f"Не удалось открыть PDF: {str(e)}")
        
        instruction = (
            "Структурированно перепиши текст с этой страницы PDF. "
            "Если там таблицы — выпиши их в виде обычного текстового представления таблицы. "
            "Присылай только текст, без лишних пояснений."
        )
        
        output_lines = []
        pages_data = []
        total_pages = len(reader.pages)
        ai_converted_pages = 0
        
        for i, page in enumerate(reader.pages, start=1):
            logger.info(f"Обрабатываем страницу {i}/{total_pages}")
            
            page_data = {
                "page_number": i,
                "text": "",
                "conversion_method": "unknown",
                "word_count": 0,
                "char_count": 0,
                "error": None
            }
            
            try:
                # Пытаемся извлечь текст стандартным способом
                text = page.extract_text() or ""
                
                if text.strip():
                    logger.info(f"Страница {i}: извлечён текст ({len(text)} символов)")
                    page_data.update({
                        "text": text,
                        "conversion_method": "standard",
                        "word_count": len(text.split()),
                        "char_count": len(text)
                    })
                    output_lines.append(f"\n\n=== Страница {i} (текст) ===\n\n{text}")
                else:
                    logger.info(f"Страница {i}: текст не извлечён — конвертирую через ИИ")
                    
                    # Конвертируем страницу в изображение
                    images = convert_from_path(
                        pdf_path, 
                        dpi=300,
                        first_page=i, 
                        last_page=i,
                        poppler_path=self.poppler_path
                    )
                    
                    if not images:
                        raise ValueError("Пустой список изображений")
                    
                    # Отправляем в LLM
                    b64_image = self.encode_image_to_base64(images[0])
                    llm_text = self.send_page_to_llm(b64_image, instruction)
                    
                    page_data.update({
                        "text": llm_text,
                        "conversion_method": "ai",
                        "word_count": len(llm_text.split()),
                        "char_count": len(llm_text)
                    })
                    
                    output_lines.append(f"\n\n=== Страница {i} (распознано ИИ) ===\n\n{llm_text}")
                    ai_converted_pages += 1
                    
            except Exception as e:
                error_msg = f"Ошибка обработки страницы {i}: {str(e)}"
                logger.error(error_msg)
                page_data.update({
                    "error": str(e),
                    "conversion_method": "error"
                })
                output_lines.append(f"\n\n=== Страница {i} (ошибка) ===\n\nОшибка: {str(e)}\n")
            
            pages_data.append(page_data)
        
        full_text = "".join(output_lines)
        
        return {
            "text": full_text,
            "metadata": {
                "total_pages": total_pages,
                "ai_converted_pages": ai_converted_pages,
                "standard_converted_pages": total_pages - ai_converted_pages,
                "total_words": len(full_text.split()),
                "total_chars": len(full_text),
                "pages": pages_data,
                "conversion_method": "hybrid" if ai_converted_pages > 0 else "standard"
            }
        }
    
    def is_pdf_scanned(self, pdf_path: str) -> bool:
        """
        Проверяет, является ли PDF отсканированным (без текстового слоя)
        
        Args:
            pdf_path: Путь к PDF файлу
            
        Returns:
            True если PDF отсканированный
        """
        try:
            reader = PdfReader(pdf_path)
            total_text_length = 0
            
            for page in reader.pages:
                text = page.extract_text() or ""
                total_text_length += len(text.strip())
            
            # Если общая длина текста меньше 50 символов, считаем PDF отсканированным
            return total_text_length < 50
            
        except Exception as e:
            logger.warning(f"Ошибка при проверке PDF: {e}")
            return True  # В случае ошибки считаем отсканированным 