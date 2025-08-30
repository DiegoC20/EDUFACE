"""
Router para endpoints de reportes y exportación
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, Dict, Any
from datetime import date, datetime, timedelta
from io import BytesIO

from ..db import get_db, Student, Attendance
from ..services.attendance_service import AttendanceService
from ..utils.pdf_generator import PDFGenerator


router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get('/summary')
def get_summary_metrics(
    period: Optional[str] = Query(None, enum=['day', 'week', 'month']),
    grade: Optional[str] = Query(None),
    section: Optional[str] = Query(None),
    start: Optional[date] = Query(None), 
    end: Optional[date] = Query(None), 
    db: Session = Depends(get_db)
):
    """Obtiene métricas resumidas con filtros"""
    
    # Definir rango de fechas según período
    if period and not start and not end:
        if period == 'day':
            start = end = date.today()
        elif period == 'week':
            start = date.today() - timedelta(days=6)
            end = date.today()
        elif period == 'month':
            start = date.today() - timedelta(days=29)
            end = date.today()
    
    # Query base para attendance con join de student
    q = db.query(Attendance).join(Student, Student.id == Attendance.student_id)
    
    # Filtrar por fechas
    if start:
        q = q.filter(Attendance.date >= start)
    if end:
        q = q.filter(Attendance.date <= end)
    
    # Filtrar por grado y sección
    if grade:
        q = q.filter(Student.grade == grade)
    if section:
        q = q.filter(Student.section == section)
    
    total = q.count()
    punctual = q.filter(Attendance.status == 'Puntual').count()
    late = q.filter(Attendance.status.in_(['Tarde', 'Muy Tarde'])).count()
    
    # Query para estudiantes totales
    student_q = db.query(Student)
    if grade:
        student_q = student_q.filter(Student.grade == grade)
    if section:
        student_q = student_q.filter(Student.section == section)
    students_total = student_q.count()
    
    punctuality = (punctual / total * 100.0) if total else 0.0
    late_pct = (late / total * 100.0) if total else 0.0
    
    # Calcular ausentes
    if start and end:
        unique_students_with_attendance = db.query(Attendance.student_id).join(
            Student, Student.id == Attendance.student_id
        )
        if start:
            unique_students_with_attendance = unique_students_with_attendance.filter(
                Attendance.date >= start
            )
        if end:
            unique_students_with_attendance = unique_students_with_attendance.filter(
                Attendance.date <= end
            )
        if grade:
            unique_students_with_attendance = unique_students_with_attendance.filter(
                Student.grade == grade
            )
        if section:
            unique_students_with_attendance = unique_students_with_attendance.filter(
                Student.section == section
            )
        
        students_with_attendance = unique_students_with_attendance.distinct().count()
        absent_students = students_total - students_with_attendance
        absent_pct = (absent_students / students_total * 100.0) if students_total else 0.0
    else:
        students_with_any_attendance = db.query(Attendance.student_id).join(
            Student, Student.id == Attendance.student_id
        )
        if grade:
            students_with_any_attendance = students_with_any_attendance.filter(
                Student.grade == grade
            )
        if section:
            students_with_any_attendance = students_with_any_attendance.filter(
                Student.section == section
            )
        
        students_with_attendance = students_with_any_attendance.distinct().count()
        absent_students = students_total - students_with_attendance
        absent_pct = (absent_students / students_total * 100.0) if students_total else 0.0
    
    return {
        "students_total": students_total,
        "records_total": total,
        "punctuality_pct": round(punctuality, 2),
        "late_pct": round(late_pct, 2),
        "absent_pct": round(absent_pct, 2),
    }


@router.get('/detailed')
def get_detailed_metrics(
    start: Optional[date] = Query(None), 
    end: Optional[date] = Query(None), 
    grade: Optional[str] = None, 
    section: Optional[str] = None, 
    db: Session = Depends(get_db)
):
    """Obtiene métricas detalladas para análisis"""
    q = db.query(Attendance, Student).join(Student, Student.id == Attendance.student_id)
    
    if start:
        q = q.filter(Attendance.date >= start)
    if end:
        q = q.filter(Attendance.date <= end)
    if grade:
        q = q.filter(Student.grade == grade)
    if section:
        q = q.filter(Student.section == section)
    
    rows = q.all()

    gender_counts: Dict[str, int] = {}
    buckets: Dict[str, int] = {
        '7:30-7:45': 0, 
        '7:45-8:00': 0, 
        '8:00-8:15': 0, 
        '8:15-8:30': 0, 
        '8:30+': 0
    }
    
    for att, st in rows:
        g = (st.gender or '-')
        gender_counts[g] = gender_counts.get(g, 0) + 1
        
        t = att.time.time()
        if t >= datetime.strptime('07:30','%H:%M').time() and t < datetime.strptime('07:45','%H:%M').time():
            buckets['7:30-7:45'] += 1
        elif t < datetime.strptime('08:00','%H:%M').time():
            buckets['7:45-8:00'] += 1
        elif t < datetime.strptime('08:15','%H:%M').time():
            buckets['8:00-8:15'] += 1
        elif t < datetime.strptime('08:30','%H:%M').time():
            buckets['8:15-8:30'] += 1
        else:
            buckets['8:30+'] += 1

    return {
        'gender_distribution': gender_counts, 
        'arrival_buckets': buckets, 
        'count': len(rows)
    }


@router.get('/export/pdf')
async def export_attendance_pdf(
    target_date: date = Query(..., alias="date"),
    grade: Optional[str] = Query(None),
    section: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Exporta reporte de asistencia en formato PDF"""
    try:
        # Generar el PDF
        pdf_generator = PDFGenerator()
        pdf_data = pdf_generator.generate_attendance_report(
            db, target_date, grade, section, status
        )
        
        # Crear respuesta de streaming
        pdf_stream = BytesIO(pdf_data)
        filename = f"reporte_asistencia_{target_date.strftime('%Y-%m-%d')}.pdf"
        
        return StreamingResponse(
            BytesIO(pdf_data),
            media_type='application/pdf',
            headers={'Content-Disposition': f'attachment; filename="{filename}"'}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar PDF: {str(e)}")
