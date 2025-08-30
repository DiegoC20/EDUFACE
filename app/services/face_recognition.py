"""
Servicio de reconocimiento facial usando DeepFace
"""
from deepface import DeepFace
from typing import Optional, Dict, Any, List
import os
from ..config.settings import settings
from ..utils.helpers import cleanup_temp_files


class FaceRecognitionService:
    """Servicio para reconocimiento facial"""
    
    def __init__(self):
        self.model_name = settings.FACE_MODEL
        self.detector_backend = settings.FACE_DETECTOR
        self.max_distance = settings.FACE_MAX_DISTANCE
        self.min_margin = settings.FACE_MIN_MARGIN
    
    def verify_faces(self, img1_path: str, img2_path: str, 
                    model_name: Optional[str] = None,
                    detector_backend: Optional[str] = None) -> Dict[str, Any]:
        """Verifica si dos rostros pertenecen a la misma persona"""
        try:
            result = DeepFace.verify(
                img1_path=img1_path, 
                img2_path=img2_path,
                model_name=model_name or self.model_name,
                detector_backend=detector_backend or self.detector_backend,
                enforce_detection=False
            )
            return result
        finally:
            cleanup_temp_files([img1_path, img2_path])
    
    def find_face(self, img_path: str, db_path: str,
                 model_name: Optional[str] = None,
                 detector_backend: Optional[str] = None,
                 distance_metric: Optional[str] = None,
                 threshold: Optional[float] = None) -> List[Dict[str, Any]]:
        """Busca un rostro en la base de datos"""
        try:
            if not os.path.isdir(db_path):
                raise ValueError(f"db_path no existe: {db_path}")
            
            # Usar configuración por defecto según el modelo
            if not distance_metric:
                distance_metric, default_threshold = settings.get_model_defaults(
                    model_name or self.model_name
                )
                if threshold is None:
                    threshold = float(settings.FACE_MAX_DISTANCE) if settings.FACE_MAX_DISTANCE else default_threshold
            
            dfs = DeepFace.find(
                img_path=img_path,
                db_path=db_path,
                model_name=model_name or self.model_name,
                detector_backend=detector_backend or self.detector_backend,
                distance_metric=distance_metric,
                enforce_detection=False
            )
            
            df = dfs[0] if isinstance(dfs, list) else dfs
            
            if threshold is not None and df is not None and not df.empty and 'distance' in df.columns:
                df = df[df['distance'] <= threshold]
            
            return df.to_dict(orient='records') if df is not None and not df.empty else []
        
        finally:
            cleanup_temp_files([img_path])
    
    def analyze_face(self, img_path: str, 
                    actions: List[str] = None,
                    detector_backend: Optional[str] = None) -> Dict[str, Any]:
        """Analiza características de un rostro"""
        if actions is None:
            actions = ["age", "gender", "emotion", "race"]
            
        try:
            result = DeepFace.analyze(
                img_path=img_path,
                actions=actions,
                detector_backend=detector_backend or self.detector_backend,
                enforce_detection=False
            )
            return {"results": result} if isinstance(result, list) else result
        finally:
            cleanup_temp_files([img_path])
    
    def recognize_for_attendance(self, img_path: str, db_path: str) -> Dict[str, Any]:
        """Reconoce un rostro específicamente para registro de asistencia"""
        try:
            distance_metric, eff_max_distance = settings.get_model_defaults(self.model_name)
            
            if settings.FACE_MAX_DISTANCE:
                eff_max_distance = float(settings.FACE_MAX_DISTANCE)
            
            dfs = DeepFace.find(
                img_path=img_path,
                db_path=db_path,
                model_name=self.model_name,
                detector_backend=self.detector_backend,
                distance_metric=distance_metric,
                enforce_detection=False
            )
            
            df = dfs[0] if isinstance(dfs, list) else dfs
            
            if df is None or df.empty:
                return {
                    "status": "unknown",
                    "reason": "no_matches",
                    "distance": None
                }
            
            # Obtener mejores coincidencias
            best = df.iloc[0]
            best_dist = float(best['distance'])
            second_dist = float(df.iloc[1]['distance']) if len(df) > 1 else None
            
            # Verificar umbral máximo
            if best_dist > eff_max_distance:
                return {
                    "status": "unknown",
                    "reason": "above_threshold",
                    "distance": best_dist
                }
            
            # Verificar margen mínimo si hay segundo candidato
            if second_dist is not None:
                margin = second_dist - best_dist
                if margin < self.min_margin:
                    return {
                        "status": "unknown",
                        "reason": "low_margin",
                        "distance": best_dist,
                        "margin": margin
                    }
            
            # Extraer información del estudiante desde el path
            identity_path = best['identity']
            # Asume estructura: db/student_code/foto.jpg
            parts = identity_path.replace('\\', '/').split('/')
            if len(parts) >= 2:
                student_code = parts[-2]
                return {
                    "status": "recognized",
                    "student_code": student_code,
                    "distance": best_dist,
                    "identity_path": identity_path
                }
            
            return {
                "status": "unknown",
                "reason": "invalid_path",
                "distance": best_dist
            }
            
        finally:
            cleanup_temp_files([img_path])
