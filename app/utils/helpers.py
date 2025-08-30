"""
Utilitarios y funciones auxiliares
"""
import tempfile
import shutil
import os
from fastapi import UploadFile
from typing import List


def save_upload_to_temp(upload: UploadFile) -> str:
    """Guarda un archivo subido en un directorio temporal"""
    suffix = os.path.splitext(upload.filename or "")[1]
    fd, path = tempfile.mkstemp(suffix=suffix or ".jpg")
    os.close(fd)
    with open(path, "wb") as f:
        shutil.copyfileobj(upload.file, f)
    return path


def ensure_directory(path: str) -> None:
    """Crea un directorio si no existe"""
    os.makedirs(path, exist_ok=True)


def cleanup_temp_files(paths: List[str]) -> None:
    """Limpia archivos temporales"""
    for path in paths:
        if path and os.path.exists(path):
            try:
                os.remove(path)
            except OSError:
                pass


def get_file_extension(filename: str) -> str:
    """Obtiene la extensión de un archivo"""
    return os.path.splitext(filename or "")[1].lower()


def is_image_file(filename: str) -> bool:
    """Verifica si un archivo es una imagen válida"""
    valid_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    return get_file_extension(filename) in valid_extensions
