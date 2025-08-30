"""
Router para endpoints de estudiantes
"""
from fastapi import APIRouter, HTTPException, Depends, Form, File, UploadFile, Path, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from ..db import get_db
from ..models.schemas import StudentCreate, StudentUpdate, StudentOut, AttendanceRecord
from ..services.student_service import StudentService
from ..services.attendance_service import AttendanceService


router = APIRouter(prefix="/students", tags=["Students"])


@router.post("/", response_model=StudentOut)
def create_student(student_data: StudentCreate, db: Session = Depends(get_db)):
    """Crea un nuevo estudiante"""
    try:
        student = StudentService.create_student(db, student_data)
        return student
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[StudentOut])
def list_students(
    grade: Optional[str] = Query(None),
    section: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Lista estudiantes con filtros opcionales"""
    return StudentService.get_students(db, grade, section, q)


@router.get("/{student_id}", response_model=StudentOut)
def get_student(student_id: int = Path(..., ge=1), db: Session = Depends(get_db)):
    """Obtiene un estudiante por ID"""
    student = StudentService.get_student_by_id(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    return student


@router.put("/{student_id}", response_model=StudentOut)
def update_student(
    student_id: int, 
    student_data: StudentUpdate, 
    db: Session = Depends(get_db)
):
    """Actualiza un estudiante existente"""
    student = StudentService.update_student(db, student_id, student_data)
    if not student:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    return student


@router.delete("/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    """Elimina un estudiante"""
    result = StudentService.delete_student(db, student_id)
    if not result["deleted"]:
        raise HTTPException(status_code=404, detail=result.get("error", "Error desconocido"))
    return result


@router.post("/form", response_model=StudentOut)
async def create_student_with_photo(
    name: str = Form(...),
    code: str = Form(...),
    grade: Optional[str] = Form(None),
    section: Optional[str] = Form(None),
    gender: Optional[str] = Form(None),
    registration_date: Optional[str] = Form(None),
    photo: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """Crea un estudiante con foto desde formulario"""
    try:
        # Generar código si no se proporciona
        if not code:
            code = name.lower().replace(' ', '_')
        
        # Procesar fecha de registro
        reg_date = None
        if registration_date:
            try:
                reg_date = date.fromisoformat(registration_date)
            except ValueError:
                reg_date = date.today()
        
        # Procesar foto si existe
        photo_path = None
        if photo and photo.filename:
            photo_data = await photo.read()
            photo_path = StudentService.save_student_photo(code, photo_data, photo.filename)
        
        # Crear estudiante
        student_data = StudentCreate(
            code=code,
            name=name,
            grade=grade,
            section=section,
            gender=gender,
            registration_date=reg_date,
            photo_path=photo_path
        )
        
        student = StudentService.create_student(db, student_data)
        return student
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.put("/{student_id}/form", response_model=StudentOut)
async def update_student_with_photo(
    student_id: int,
    name: Optional[str] = Form(None),
    grade: Optional[str] = Form(None),
    section: Optional[str] = Form(None),
    gender: Optional[str] = Form(None),
    registration_date: Optional[str] = Form(None),
    photo: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """Actualiza un estudiante con foto desde formulario"""
    try:
        # Verificar que el estudiante existe
        student = StudentService.get_student_by_id(db, student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Estudiante no encontrado")
        
        # Preparar datos de actualización
        update_data = {}
        if name is not None:
            update_data["name"] = name
        if grade is not None:
            update_data["grade"] = grade
        if section is not None:
            update_data["section"] = section
        if gender is not None:
            update_data["gender"] = gender
        if registration_date:
            try:
                update_data["registration_date"] = date.fromisoformat(registration_date)
            except ValueError:
                pass
        
        # Procesar nueva foto si existe
        if photo and photo.filename:
            photo_data = await photo.read()
            photo_path = StudentService.save_student_photo(student.code, photo_data, photo.filename)
            update_data["photo_path"] = photo_path
        
        # Actualizar estudiante
        student_update = StudentUpdate(**update_data)
        updated_student = StudentService.update_student(db, student_id, student_update)
        
        return updated_student
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get("/{student_id}/attendance", response_model=List[AttendanceRecord])
def get_student_attendance(
    student_id: int = Path(..., ge=1),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Obtiene el historial de asistencia de un estudiante"""
    return AttendanceService.get_student_attendance_history(db, student_id, limit)
