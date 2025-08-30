"""
Router para endpoints de reconocimiento facial
"""
from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Optional
from ..services.face_recognition import FaceRecognitionService
from ..utils.helpers import save_upload_to_temp


router = APIRouter(prefix="/face", tags=["Face Recognition"])
face_service = FaceRecognitionService()


@router.post("/verify")
async def verify_faces(
    img1: UploadFile = File(...), 
    img2: UploadFile = File(...),
    model_name: str = Form("VGG-Face"), 
    detector_backend: str = Form("opencv")
):
    """Verifica si dos rostros pertenecen a la misma persona"""
    try:
        img1_path = save_upload_to_temp(img1)
        img2_path = save_upload_to_temp(img2)
        
        result = face_service.verify_faces(
            img1_path, img2_path, model_name, detector_backend
        )
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recognize")
async def recognize_face(
    img: UploadFile = File(...), 
    db_path: str = Form("db"),
    model_name: str = Form("VGG-Face"), 
    detector_backend: str = Form("opencv"),
    distance_metric: str = Form("cosine"), 
    threshold: Optional[float] = Form(None)
):
    """Busca un rostro en la base de datos"""
    try:
        img_path = save_upload_to_temp(img)
        matches = face_service.find_face(
            img_path, db_path, model_name, detector_backend, 
            distance_metric, threshold
        )
        return {"matches": matches}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze")
async def analyze_face(
    img: UploadFile = File(...),
    actions: List[str] = Form(["age", "gender", "emotion", "race"]),
    detector_backend: str = Form("opencv")
):
    """Analiza características faciales"""
    try:
        img_path = save_upload_to_temp(img)
        result = face_service.analyze_face(img_path, actions, detector_backend)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
