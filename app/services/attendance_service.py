"""
Servicio de gestión de asistencia
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any, Optional
from datetime import date, datetime, timedelta
from ..db import Student, Attendance
from ..models.schemas import AttendanceRecord, MetricsResponse


class AttendanceService:
    """Servicio para gestión de asistencia"""
    
    @staticmethod
    def mark_attendance(db: Session, student_id: int, 
                       attendance_time: datetime = None) -> Attendance:
        """Marca la asistencia de un estudiante"""
        if attendance_time is None:
            attendance_time = datetime.now()
        
        # Determinar estado basado en la hora
        time_only = attendance_time.time()
        if time_only <= datetime.strptime('07:45', '%H:%M').time():
            status = 'Puntual'
        else:
            status = 'Tarde'
        
        attendance = Attendance(
            student_id=student_id,
            time=attendance_time,
            date=attendance_time.date(),
            status=status
        )
        
        db.add(attendance)
        db.commit()
        db.refresh(attendance)
        return attendance
    
    @staticmethod
    def get_today_attendance(db: Session) -> List[AttendanceRecord]:
        """Obtiene la asistencia del día actual"""
        today = date.today()
        rows = (
            db.query(Attendance, Student)
            .join(Student, Student.id == Attendance.student_id)
            .filter(Attendance.date == today)
            .order_by(Attendance.time.desc())
            .all()
        )
        
        return [
            AttendanceRecord(
                student_id=att.student_id,
                student_name=st.name,
                student_code=st.code,
                time=att.time.strftime('%H:%M:%S'),
                status=att.status,
                date=str(att.date),
                distance=None,
                grade=st.grade,
                section=st.section
            )
            for att, st in rows
        ]
    
    @staticmethod
    def get_recent_attendance(db: Session, limit: int = 20) -> List[AttendanceRecord]:
        """Obtiene los registros recientes de asistencia"""
        rows = (
            db.query(Attendance, Student)
            .join(Student, Student.id == Attendance.student_id)
            .order_by(Attendance.time.desc())
            .limit(limit)
            .all()
        )
        
        return [
            AttendanceRecord(
                student_id=att.student_id,
                student_name=st.name,
                student_code=st.code,
                time=att.time.strftime('%H:%M:%S'),
                status=att.status,
                date=str(att.date),
                distance=None,
                grade=st.grade,
                section=st.section
            )
            for att, st in rows
        ]
    
    @staticmethod
    def get_student_attendance_history(db: Session, student_id: int, 
                                     limit: int = 50) -> List[AttendanceRecord]:
        """Obtiene el historial de asistencia de un estudiante"""
        student = db.get(Student, student_id)
        if not student:
            return []
        
        rows = (
            db.query(Attendance)
            .filter(Attendance.student_id == student_id)
            .order_by(Attendance.time.desc())
            .limit(limit)
            .all()
        )
        
        return [
            AttendanceRecord(
                student_id=att.student_id,
                student_name=student.name,
                student_code=student.code,
                time=att.time.strftime('%H:%M:%S'),
                status=att.status,
                date=str(att.date),
                distance=None,
                grade=student.grade,
                section=student.section
            )
            for att in rows
        ]
    
    @staticmethod
    def get_today_metrics(db: Session) -> MetricsResponse:
        """Obtiene las métricas del día actual"""
        today = date.today()
        total_students = db.query(Student).count()
        
        attendance_query = db.query(Attendance).filter(Attendance.date == today)
        total_today = attendance_query.count()
        punctual = attendance_query.filter(Attendance.status == 'Puntual').count()
        late = attendance_query.filter(Attendance.status == 'Tarde').count()
        absent = max(total_students - total_today, 0)
        
        return MetricsResponse(
            total_today=total_today,
            punctual_today=punctual,
            late_today=late,
            absent_today=absent
        )
    
    @staticmethod
    def get_weekly_metrics(db: Session) -> Dict[str, List]:
        """Obtiene las métricas de la última semana"""
        labels = []
        attendance_pct = []
        total_students = db.query(Student).count()
        
        for i in range(6, -1, -1):
            target_date = date.today() - timedelta(days=i)
            labels.append(target_date.strftime('%a'))
            
            total = db.query(Attendance).filter(Attendance.date == target_date).count()
            pct = (total / total_students * 100.0) if total_students > 0 else 0.0
            attendance_pct.append(round(pct, 2))
        
        return {"labels": labels, "attendance_pct": attendance_pct}
    
    @staticmethod
    def get_attendance_by_grade(db: Session, target_date: date = None) -> Dict[str, int]:
        """Obtiene la asistencia agrupada por grado"""
        if target_date is None:
            target_date = date.today()
        
        rows = (
            db.query(Attendance, Student)
            .join(Student, Student.id == Attendance.student_id)
            .filter(Attendance.date == target_date)
            .all()
        )
        
        grade_counts = {}
        for att, student in rows:
            grade = student.grade or 'Sin grado'
            grade_counts[grade] = grade_counts.get(grade, 0) + 1
        
        return grade_counts
    
    @staticmethod
    def clear_attendance_by_date(db: Session, target_date: date) -> int:
        """Elimina registros de asistencia de una fecha específica"""
        deleted = db.query(Attendance).filter(Attendance.date == target_date).delete(
            synchronize_session=False
        )
        db.commit()
        return deleted
    
    @staticmethod
    def clear_all_attendance(db: Session) -> int:
        """Elimina todos los registros de asistencia"""
        deleted = db.query(Attendance).delete(synchronize_session=False)
        db.commit()
        return deleted
