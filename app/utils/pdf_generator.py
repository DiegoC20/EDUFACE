"""
Generador de reportes PDF
"""
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from sqlalchemy.orm import Session
from typing import Optional, List, Tuple, Any
from datetime import date
from io import BytesIO

from ..db import Student, Attendance


class AbsentAttendance:
    """Clase helper para representar estudiantes ausentes"""
    def __init__(self, student: Student, target_date: date):
        self.student_id = student.id
        self.date = target_date
        self.time = None
        self.status = 'Ausente'
        self.student = student


class PDFGenerator:
    """Generador de reportes PDF para el sistema EDUFACE"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configura estilos personalizados para el PDF"""
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2c3e50')
        )
        
        self.subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#34495e')
        )
        
        self.info_style = ParagraphStyle(
            'InfoStyle',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=12,
            alignment=TA_LEFT
        )
    
    def generate_attendance_report(
        self, 
        db: Session, 
        target_date: date,
        grade: Optional[str] = None,
        section: Optional[str] = None,
        status: Optional[str] = None
    ) -> bytes:
        """Genera un reporte de asistencia en PDF"""
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72,
                               topMargin=72, bottomMargin=18)
        
        # Construir el contenido del PDF
        story = []
        
        # Título
        title = Paragraph("REPORTE DE ASISTENCIA - EDUFACE", self.title_style)
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Información del reporte
        info_lines = [
            f"<b>Fecha del reporte:</b> {target_date.strftime('%d/%m/%Y')}",
            f"<b>Grado:</b> {grade or 'Todos los grados'}",
            f"<b>Sección:</b> {section or 'Todas las secciones'}",
            f"<b>Estado:</b> {status or 'Todos los estados'}",
            f"<b>Generado el:</b> {date.today().strftime('%d/%m/%Y')}"
        ]
        
        for line in info_lines:
            story.append(Paragraph(line, self.info_style))
        
        story.append(Spacer(1, 20))
        
        # Obtener datos
        attendance_data, summary = self._get_attendance_data(
            db, target_date, grade, section, status
        )
        
        # Resumen estadístico
        summary_title = Paragraph("RESUMEN ESTADÍSTICO", self.subtitle_style)
        story.append(summary_title)
        
        summary_table_data = [
            ['Métrica', 'Cantidad'],
            ['Total de estudiantes', str(summary['total_students'])],
            ['Presentes', str(summary['present'])],
            ['Ausentes', str(summary['absent'])],
            ['Puntuales', str(summary['punctual'])],
            ['Tardanzas', str(summary['late'])]
        ]
        
        summary_table = Table(summary_table_data, colWidths=[3*inch, 1.5*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 30))
        
        # Tabla de asistencia
        detail_title = Paragraph("DETALLE DE ASISTENCIA", self.subtitle_style)
        story.append(detail_title)
        
        if attendance_data:
            # Encabezados de la tabla
            table_data = [['Código', 'Nombre', 'Grado', 'Sección', 'Hora', 'Estado']]
            
            # Datos de asistencia
            for record in attendance_data:
                if hasattr(record, 'student'):
                    # Es un registro de asistencia real
                    student = record.student
                    time_str = record.time.strftime('%H:%M:%S') if record.time else '-'
                else:
                    # Es un estudiante ausente (AbsentAttendance)
                    student = record.student
                    time_str = '-'
                
                table_data.append([
                    student.code or '-',
                    student.name or '-',
                    student.grade or '-',
                    student.section or '-',
                    time_str,
                    record.status
                ])
            
            # Crear tabla
            detail_table = Table(table_data, colWidths=[1*inch, 2.5*inch, 0.8*inch, 0.8*inch, 1*inch, 1*inch])
            detail_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ecc71')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
            ]))
            
            story.append(detail_table)
        else:
            no_data = Paragraph("No se encontraron registros para los filtros especificados.", self.info_style)
            story.append(no_data)
        
        # Construir PDF
        doc.build(story)
        
        pdf_data = buffer.getvalue()
        buffer.close()
        
        return pdf_data
    
    def _get_attendance_data(
        self, 
        db: Session, 
        target_date: date,
        grade: Optional[str] = None,
        section: Optional[str] = None,
        status: Optional[str] = None
    ) -> Tuple[List[Any], dict]:
        """Obtiene los datos de asistencia y calcula estadísticas"""
        
        print(f"[PDF DEBUG] Filtros: date={target_date}, grade={grade}, section={section}, status={status}")
        
        # Query base para estudiantes
        students_query = db.query(Student)
        if grade:
            students_query = students_query.filter(Student.grade == grade)
        if section:
            students_query = students_query.filter(Student.section == section)
        
        all_students = students_query.all()
        total_students = len(all_students)
        
        print(f"[PDF DEBUG] Total estudiantes encontrados: {total_students}")
        
        if status == 'Ausente':
            print("[PDF DEBUG] Generando reporte solo de AUSENTES")
            # Solo estudiantes ausentes
            attendance_query = db.query(Attendance).filter(Attendance.date == target_date)
            if grade or section:
                attendance_query = attendance_query.join(Student, Student.id == Attendance.student_id)
                if grade:
                    attendance_query = attendance_query.filter(Student.grade == grade)
                if section:
                    attendance_query = attendance_query.filter(Student.section == section)
            
            present_student_ids = {att.student_id for att in attendance_query.all()}
            absent_students = [s for s in all_students if s.id not in present_student_ids]
            
            records = [AbsentAttendance(student, target_date) for student in absent_students]
            
            summary = {
                'total_students': total_students,
                'present': total_students - len(absent_students),
                'absent': len(absent_students),
                'punctual': 0,
                'late': 0
            }
            
            print(f"[PDF DEBUG] Estudiantes ausentes: {len(absent_students)}")
            
        elif not status:  # "Todos los estados"
            print("[PDF DEBUG] Generando reporte de TODOS los estados (incluyendo ausentes)")
            
            # Obtener registros de asistencia
            attendance_query = db.query(Attendance, Student).join(
                Student, Student.id == Attendance.student_id
            ).filter(Attendance.date == target_date)
            
            if grade:
                attendance_query = attendance_query.filter(Student.grade == grade)
            if section:
                attendance_query = attendance_query.filter(Student.section == section)
            
            attendance_records = attendance_query.all()
            present_student_ids = {att.student_id for att, _ in attendance_records}
            
            # Estudiantes ausentes
            absent_students = [s for s in all_students if s.id not in present_student_ids]
            
            # Combinar registros
            records = []
            
            # Agregar registros de asistencia
            for att, student in attendance_records:
                # Crear objeto que tenga tanto attendance como student
                record = type('AttendanceRecord', (), {
                    'student_id': att.student_id,
                    'date': att.date,
                    'time': att.time,
                    'status': att.status,
                    'student': student
                })()
                records.append(record)
            
            # Agregar estudiantes ausentes
            for student in absent_students:
                records.append(AbsentAttendance(student, target_date))
            
            # Calcular estadísticas
            punctual = sum(1 for att, _ in attendance_records if att.status == 'Puntual')
            late = sum(1 for att, _ in attendance_records if att.status in ['Tarde', 'Muy Tarde'])
            
            summary = {
                'total_students': total_students,
                'present': len(attendance_records),
                'absent': len(absent_students),
                'punctual': punctual,
                'late': late
            }
            
            print(f"[PDF DEBUG] Total registros (presente + ausentes): {len(records)}")
            
        else:
            print(f"[PDF DEBUG] Generando reporte para estado específico: {status}")
            # Estado específico (Puntual, Tarde, etc.)
            attendance_query = db.query(Attendance, Student).join(
                Student, Student.id == Attendance.student_id
            ).filter(Attendance.date == target_date, Attendance.status == status)
            
            if grade:
                attendance_query = attendance_query.filter(Student.grade == grade)
            if section:
                attendance_query = attendance_query.filter(Student.section == section)
            
            attendance_records = attendance_query.all()
            
            records = []
            for att, student in attendance_records:
                record = type('AttendanceRecord', (), {
                    'student_id': att.student_id,
                    'date': att.date,
                    'time': att.time,
                    'status': att.status,
                    'student': student
                })()
                records.append(record)
            
            # Calcular estadísticas básicas
            all_attendance = db.query(Attendance).filter(Attendance.date == target_date)
            if grade or section:
                all_attendance = all_attendance.join(Student, Student.id == Attendance.student_id)
                if grade:
                    all_attendance = all_attendance.filter(Student.grade == grade)
                if section:
                    all_attendance = all_attendance.filter(Student.section == section)
            
            all_att_records = all_attendance.all()
            present_count = len(all_att_records)
            punctual = sum(1 for att in all_att_records if att.status == 'Puntual')
            late = sum(1 for att in all_att_records if att.status in ['Tarde', 'Muy Tarde'])
            
            summary = {
                'total_students': total_students,
                'present': present_count,
                'absent': total_students - present_count,
                'punctual': punctual,
                'late': late
            }
        
        # Ordenar registros por nombre del estudiante
        records.sort(key=lambda x: x.student.name or '')
        
        return records, summary
