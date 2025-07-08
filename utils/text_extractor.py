import os
import fitz  # PyMuPDF
from docx import Document
from typing import List

class TextExtractor:
    @staticmethod
    def extract_text(file_path: str) -> str:
        """Извлекает текст из файла в зависимости от его расширения"""
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.pdf':
            return TextExtractor._extract_from_pdf(file_path)
        elif file_extension == '.docx':
            return TextExtractor._extract_from_docx(file_path)
        elif file_extension == '.txt':
            return TextExtractor._extract_from_txt(file_path)
        else:
            raise ValueError(f"Неподдерживаемый формат файла: {file_extension}")
    
    @staticmethod
    def _extract_from_pdf(file_path: str) -> str:
        """Извлекает текст из PDF файла"""
        text = ""
        try:
            doc = fitz.open(file_path)
            for page in doc:
                text += page.get_text()
            doc.close()
        except Exception as e:
            raise Exception(f"Ошибка при извлечении текста из PDF: {str(e)}")
        return text
    
    @staticmethod
    def _extract_from_docx(file_path: str) -> str:
        """Извлекает текст из DOCX файла"""
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            raise Exception(f"Ошибка при извлечении текста из DOCX: {str(e)}")
    
    @staticmethod
    def _extract_from_txt(file_path: str) -> str:
        """Извлекает текст из TXT файла"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            raise Exception(f"Ошибка при извлечении текста из TXT: {str(e)}")
    
    @staticmethod
    def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Разбивает текст на чанки с перекрытием"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Если это не последний чанк, ищем ближайший пробел для разрыва
            if end < len(text):
                # Ищем последний пробел в пределах чанка
                last_space = text.rfind(' ', start, end)
                if last_space > start:
                    end = last_space
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Следующий чанк начинается с учетом перекрытия
            start = end - overlap
            if start >= len(text):
                break
        
        return chunks 