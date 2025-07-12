import os
import uuid
from typing import Dict, Any, Tuple
from utils.text_extractor import TextExtractor

class FileProcessor:
    """Сервис для обработки загруженных файлов"""
    
    def __init__(self, upload_dir: str):
        self.upload_dir = upload_dir
    
    def process_uploaded_file(self, file_content: bytes, original_filename: str) -> Dict[str, Any]:
        """
        Обрабатывает загруженный файл:
        1. Сохраняет оригинал
        2. Конвертирует в txt
        3. Возвращает метаданные
        
        Returns:
            Dict с file_id, путями к файлам, текстом и метаданными
        """
        # Проверяем формат файла
        file_extension = os.path.splitext(original_filename)[1].lower()
        allowed_extensions = {'.pdf', '.docx', '.txt'}
        
        if file_extension not in allowed_extensions:
            raise ValueError(f"Неподдерживаемый формат файла: {file_extension}")
        
        # Генерируем уникальный ID
        file_id = str(uuid.uuid4())
        
        # Формируем пути к файлам
        original_path = os.path.join(self.upload_dir, f"{file_id}_original{file_extension}")
        txt_path = os.path.join(self.upload_dir, f"{file_id}.txt")
        
        try:
            # Сохраняем оригинал
            with open(original_path, "wb") as buffer:
                buffer.write(file_content)
            
            # Извлекаем текст и сохраняем как txt
            text_data = TextExtractor.extract_text_with_metadata(original_path)
            text = text_data['text']
            metadata = text_data['metadata']
            
            with open(txt_path, "w", encoding="utf-8") as txt_file:
                txt_file.write(text)
            
            # Формируем результат
            result = {
                "file_id": file_id,
                "original_filename": original_filename,
                "original_path": original_path,
                "txt_path": txt_path,
                "text": text,
                "file_size": len(file_content),
                "file_type": file_extension,
                "extraction_metadata": metadata
            }
            
            return result
            
        except Exception as e:
            # Очищаем файлы в случае ошибки
            self._cleanup_files(original_path, txt_path)
            raise Exception(f"Ошибка при обработке файла: {str(e)}")
    
    def delete_file_versions(self, file_id: str) -> bool:
        """
        Удаляет все версии файла (оригинал и txt)
        
        Args:
            file_id: ID файла для удаления
            
        Returns:
            True если файлы удалены, False если не найдены
        """
        deleted = False
        
        for filename in os.listdir(self.upload_dir):
            if filename.startswith(file_id):
                file_path = os.path.join(self.upload_dir, filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
                    deleted = True
        
        return deleted
    
    def get_file_info(self, file_id: str) -> Dict[str, Any]:
        """
        Получает информацию о файле
        
        Args:
            file_id: ID файла
            
        Returns:
            Dict с информацией о файле
        """
        file_info = {
            "file_id": file_id,
            "original_path": None,
            "txt_path": None,
            "exists": False
        }
        
        for filename in os.listdir(self.upload_dir):
            if filename.startswith(file_id):
                file_path = os.path.join(self.upload_dir, filename)
                if os.path.exists(file_path):
                    file_info["exists"] = True
                    
                    if filename.endswith('.txt'):
                        file_info["txt_path"] = file_path
                    else:
                        file_info["original_path"] = file_path
        
        return file_info
    
    def _cleanup_files(self, *file_paths):
        """Удаляет файлы в случае ошибки"""
        for file_path in file_paths:
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception:
                    pass  # Игнорируем ошибки при удалении 