"""
Modelos Pydantic para validación de datos
"""
from pydantic import BaseModel
from typing import Optional
from datetime import date


class StudentBase(BaseModel):
    """Modelo base para estudiante"""
    code: str
    name: str
    grade: Optional[str] = None
    section: Optional[str] = None
    gender: Optional[str] = None
    registration_date: Optional[date] = None
    photo_path: Optional[str] = None


class StudentCreate(StudentBase):
    """Modelo para crear estudiante"""
    pass


class StudentUpdate(BaseModel):
    """Modelo para actualizar estudiante"""
    name: Optional[str] = None
    grade: Optional[str] = None
    section: Optional[str] = None
    gender: Optional[str] = None
    registration_date: Optional[date] = None
    photo_path: Optional[str] = None


class StudentOut(StudentBase):
    """Modelo de respuesta para estudiante"""
    id: int

    class Config:
        from_attributes = True


class AttendanceRecord(BaseModel):
    """Modelo para registro de asistencia"""
    student_id: int
    student_name: str
    student_code: str
    time: str
    status: str
    date: str
    distance: Optional[float] = None
    grade: Optional[str] = None
    section: Optional[str] = None


class MetricsResponse(BaseModel):
    """Modelo para respuesta de métricas"""
    total_today: int
    punctual_today: int
    late_today: int
    absent_today: int


class FaceRecognitionResult(BaseModel):
    """Modelo para resultado de reconocimiento facial"""
    status: str
    student_id: Optional[int] = None
    student_name: Optional[str] = None
    distance: Optional[float] = None
    reason: Optional[str] = None
    margin: Optional[float] = None
