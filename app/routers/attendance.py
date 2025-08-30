"""
Router para endpoints de asistencia
"""
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime
from ..db import get_db
from ..models.schemas import AttendanceRecord, MetricsResponse, FaceRecognitionResult
from ..services.attendance_service import AttendanceService
from ..services.student_service import StudentService
from ..services.face_recognition import FaceRecognitionService
from ..utils.helpers import save_upload_to_temp
from ..config.settings import settings


router = APIRouter(prefix="/attendance", tags=["Attendance"])
face_service = FaceRecognitionService()


@router.post("/mark")
async def mark_attendance(
    img: UploadFile = File(...),
    db_path: str = Form('db'),
    detector_backend: str = Form(settings.FACE_DETECTOR),
    model_name: str = Form(settings.FACE_MODEL),
    max_distance: Optional[float] = Form(None),
    min_margin: float = Form(settings.FACE_MIN_MARGIN),
    db: Session = Depends(get_db)
):
    """Marca asistencia usando reconocimiento facial"""
    img_path = save_upload_to_temp(img)
    
    try:
        # Reconocer rostro
        recognition_result = face_service.recognize_for_attendance(img_path, db_path)
        
        if recognition_result["status"] != "recognized":
            return {
                "status": "unknown",
                "reason": recognition_result.get("reason", "no_match"),
                "distance": recognition_result.get("distance"),
                "margin": recognition_result.get("margin")
            }
        
        # Buscar estudiante por código
        student_code = recognition_result["student_code"]
        student = StudentService.get_student_by_code(db, student_code)
        
        if not student:
            return {
                "status": "unknown",
                "reason": "student_not_found",
                "student_code": student_code
            }
        
        # Verificar si ya marcó asistencia hoy
        today = date.today()
        from ..db import Attendance
        existing_attendance = db.query(Attendance).filter(
            Attendance.student_id == student.id,
            Attendance.date == today
        ).first()
        
        if existing_attendance:
            return {
                "status": "already_marked",
                "student_id": student.id,
                "student_name": student.name,
                "existing_time": existing_attendance.time.strftime('%H:%M:%S'),
                "existing_status": existing_attendance.status
            }
        
        # Marcar asistencia
        attendance = AttendanceService.mark_attendance(db, student.id)
        
        return {
            "status": "success",
            "student_id": student.id,
            "student_name": student.name,
            "student_code": student.code,
            "time": attendance.time.strftime('%H:%M:%S'),
            "attendance_status": attendance.status,  # Cambiar nombre del campo
            "distance": recognition_result.get("distance"),
            "message": f"¡{student.name} registrado exitosamente!"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/today", response_model=List[AttendanceRecord])
def get_today_attendance(db: Session = Depends(get_db)):
    """Obtiene la asistencia del día actual"""
    return AttendanceService.get_today_attendance(db)


@router.get("/recent", response_model=List[AttendanceRecord])
def get_recent_attendance(
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Obtiene los registros recientes de asistencia"""
    return AttendanceService.get_recent_attendance(db, limit)


@router.get("/metrics/today", response_model=MetricsResponse)
def get_today_metrics(db: Session = Depends(get_db)):
    """Obtiene las métricas del día actual"""
    return AttendanceService.get_today_metrics(db)


@router.get("/metrics/weekly")
def get_weekly_metrics(db: Session = Depends(get_db)):
    """Obtiene las métricas de la última semana"""
    return AttendanceService.get_weekly_metrics(db)


@router.get("/metrics/by-grade")
def get_metrics_by_grade(db: Session = Depends(get_db)):
    """Obtiene la asistencia agrupada por grado"""
    return AttendanceService.get_attendance_by_grade(db)
