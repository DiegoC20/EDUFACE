"""
Servicio de gestión de estudiantes
"""
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import date
import os
import shutil
from ..db import Student
from ..models.schemas import StudentCreate, StudentUpdate
from ..config.settings import settings
from ..utils.helpers import ensure_directory, is_image_file


class StudentService:
    """Servicio para gestión de estudiantes"""
    
    @staticmethod
    def create_student(db: Session, student_data: StudentCreate) -> Student:
        """Crea un nuevo estudiante"""
        # Verificar si el código ya existe
        existing = db.query(Student).filter_by(code=student_data.code).first()
        if existing:
            raise ValueError(f"El código {student_data.code} ya existe")
        
        student = Student(
            code=student_data.code,
            name=student_data.name,
            grade=student_data.grade,
            section=student_data.section,
            gender=student_data.gender,
            registration_date=student_data.registration_date,
            photo_path=student_data.photo_path,
        )
        
        db.add(student)
        db.commit()
        db.refresh(student)
        return student
    
    @staticmethod
    def get_students(db: Session, grade: Optional[str] = None, 
                    section: Optional[str] = None, 
                    search_query: Optional[str] = None) -> List[Student]:
        """Obtiene lista de estudiantes con filtros opcionales"""
        query = db.query(Student)
        
        if grade:
            query = query.filter(Student.grade == grade)
        if section:
            query = query.filter(Student.section == section)
        if search_query:
            like_pattern = f"%{search_query}%"
            query = query.filter(
                (Student.name.like(like_pattern)) | 
                (Student.code.like(like_pattern))
            )
        
        return query.order_by(Student.name).all()
    
    @staticmethod
    def get_student_by_id(db: Session, student_id: int) -> Optional[Student]:
        """Obtiene un estudiante por ID"""
        return db.get(Student, student_id)
    
    @staticmethod
    def get_student_by_code(db: Session, code: str) -> Optional[Student]:
        """Obtiene un estudiante por código"""
        return db.query(Student).filter_by(code=code).first()
    
    @staticmethod
    def update_student(db: Session, student_id: int, 
                      student_data: StudentUpdate) -> Optional[Student]:
        """Actualiza un estudiante existente"""
        student = db.get(Student, student_id)
        if not student:
            return None
        
        update_data = student_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(student, field, value)
        
        db.commit()
        db.refresh(student)
        return student
    
    @staticmethod
    def delete_student(db: Session, student_id: int) -> Dict[str, Any]:
        """Elimina un estudiante y sus archivos asociados"""
        student = db.get(Student, student_id)
        if not student:
            return {"deleted": False, "error": "Estudiante no encontrado"}
        
        # Eliminar archivos físicos
        files_cleaned = StudentService._cleanup_student_files(student.code)
        
        # Eliminar de la base de datos
        db.delete(student)
        db.commit()
        
        return {
            "deleted": True, 
            "files_cleaned": files_cleaned,
            "student_code": student.code
        }
    
    @staticmethod
    def _cleanup_student_files(student_code: str) -> bool:
        """Limpia los archivos asociados a un estudiante"""
        try:
            # Eliminar carpeta en db/
            db_folder = os.path.join(settings.DB_FACES_DIR, student_code)
            if os.path.exists(db_folder):
                shutil.rmtree(db_folder)
            
            # Eliminar foto en students/
            possible_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
            for ext in possible_extensions:
                photo_path = os.path.join(settings.STUDENTS_MEDIA_DIR, f"{student_code}{ext}")
                if os.path.exists(photo_path):
                    os.remove(photo_path)
                    break
            
            return True
        except Exception:
            return False
    
    @staticmethod
    def save_student_photo(student_code: str, photo_data: bytes, 
                          original_filename: str) -> str:
        """Guarda la foto de un estudiante"""
        if not is_image_file(original_filename):
            raise ValueError("El archivo no es una imagen válida")
        
        # Crear directorios si no existen
        ensure_directory(settings.STUDENTS_MEDIA_DIR)
        ensure_directory(os.path.join(settings.DB_FACES_DIR, student_code))
        
        # Determinar extensión
        extension = os.path.splitext(original_filename)[1].lower() or '.jpg'
        
        # Guardar en students/ (para servir estáticamente)
        students_photo_path = os.path.join(settings.STUDENTS_MEDIA_DIR, f"{student_code}{extension}")
        with open(students_photo_path, 'wb') as f:
            f.write(photo_data)
        
        # Guardar en db/student_code/ (para DeepFace)
        db_photo_path = os.path.join(settings.DB_FACES_DIR, student_code, f"profile{extension}")
        with open(db_photo_path, 'wb') as f:
            f.write(photo_data)
        
        return f"/media/students/{student_code}{extension}"
