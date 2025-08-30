"""
Configuración central de la aplicación EDUFACE
"""
import os
from typing import Optional, Tuple


class Settings:
    """Configuración de la aplicación"""
    
    # API Configuration
    TITLE: str = "EDUFACE API"
    VERSION: str = "1.0.0"
    
    # Face Recognition Configuration
    FACE_MODEL: str = os.getenv('FACE_MODEL', 'ArcFace')
    FACE_DETECTOR: str = os.getenv('FACE_DETECTOR', 'opencv')
    FACE_MAX_DISTANCE: Optional[str] = os.getenv('FACE_MAX_DISTANCE', '1.5')  # Más permisivo
    FACE_MIN_MARGIN: float = float(os.getenv('FACE_MIN_MARGIN', '0.01'))  # Menos restrictivo
    
    # Database Configuration
    DATABASE_URL: str = "sqlite:///./attendance.sqlite3"
    
    # File paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(__file__))
    STATIC_DIR: str = os.path.join(BASE_DIR, "static")
    STUDENTS_MEDIA_DIR: str = os.path.abspath(os.path.join(BASE_DIR, '..', 'students'))
    DB_FACES_DIR: str = os.path.abspath(os.path.join(BASE_DIR, '..', 'db'))
    
    @staticmethod
    def get_model_defaults(model_name: str) -> Tuple[str, float]:
        """Obtiene configuración por defecto según el modelo de reconocimiento"""
        name = (model_name or '').lower()
        if 'arc' in name:  # ArcFace
            return 'euclidean_l2', 1.20
        if 'facenet' in name:  # Facenet/Facenet512
            return 'cosine', 0.30
        # VGG-Face y otros
        return 'cosine', 0.30


settings = Settings()
