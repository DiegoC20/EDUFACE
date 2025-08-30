"""
Router para endpoints administrativos
"""
from fastapi import APIRouter, HTTPException, Depends, Form
from sqlalchemy.orm import Session
from datetime import date
from ..db import get_db
from ..services.attendance_service import AttendanceService
from ..services.student_service import StudentService


router = APIRouter(prefix="/admin", tags=["Administration"])


@router.post('/attendance/clear-today')
@router.get('/attendance/clear-today')
def clear_today_attendance(db: Session = Depends(get_db)):
    """Elimina todos los registros de asistencia del día actual"""
    today = date.today()
    deleted = AttendanceService.clear_attendance_by_date(db, today)
    return {"deleted": deleted, "date": str(today)}


@router.post('/attendance/clear-all')
@router.get('/attendance/clear-all')
def clear_all_attendance(db: Session = Depends(get_db)):
    """Elimina todos los registros de asistencia"""
    deleted = AttendanceService.clear_all_attendance(db)
    return {"deleted": deleted}


@router.post('/attendance/clear-date')
def clear_date_attendance(target: str = Form(...), db: Session = Depends(get_db)):
    """Elimina registros de asistencia de una fecha específica"""
    try:
        target_date = date.fromisoformat(target)
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido (use YYYY-MM-DD)")
    
    deleted = AttendanceService.clear_attendance_by_date(db, target_date)
    return {"deleted": deleted, "date": str(target_date)}


@router.get('/attendance/counts')
def get_attendance_counts(db: Session = Depends(get_db)):
    """Obtiene conteos generales de asistencia"""
    from ..db import Attendance
    today = date.today()
    
    total = db.query(Attendance).count()
    today_count = db.query(Attendance).filter(Attendance.date == today).count()
    
    return {
        "total": total,
        "today": today_count,
        "date": str(today)
    }


@router.post('/students/clear-all')
@router.get('/students/clear-all')
def clear_all_students(db: Session = Depends(get_db)):
    """Elimina todos los estudiantes (CUIDADO: operación destructiva)"""
    from ..db import Student
    
    # Obtener todos los estudiantes para limpiar archivos
    students = db.query(Student).all()
    deleted_count = len(students)
    
    # Limpiar archivos de cada estudiante
    for student in students:
        StudentService._cleanup_student_files(student.code)
    
    # Eliminar de la base de datos
    db.query(Student).delete(synchronize_session=False)
    db.commit()
    
    return {
        "deleted": deleted_count,
        "files_cleaned": True,
        "message": "Todos los estudiantes han sido eliminados"
    }
