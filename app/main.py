"""
Aplicación principal EDUFACE - Refactorizada con arquitectura modular
"""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os

# Importaciones locales
from .config.settings import settings
from .db import init_db
from .utils.helpers import ensure_directory
from .routers import face_recognition, students, attendance
from .routers.admin import router as admin_router
from .routers.reports import router as reports_router


def create_app() -> FastAPI:
    """Factory para crear la aplicación FastAPI"""
    app = FastAPI(
        title=settings.TITLE,
        version=settings.VERSION,
        description="Sistema de control de asistencia por reconocimiento facial"
    )
    
    # Configurar middleware CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Configurar archivos estáticos y templates
    setup_static_files(app)
    
    # Configurar rutas
    setup_routes(app)
    
    # Configurar eventos de inicio
    setup_startup_events(app)
    
    return app


def setup_static_files(app: FastAPI) -> None:
    """Configura los archivos estáticos"""
    # Directorio static para CSS, JS, etc.
    static_path = os.path.join(os.path.dirname(__file__), "static")
    if os.path.isdir(static_path):
        app.mount("/static", StaticFiles(directory=static_path), name="static")
    
    # Directorio de fotos de estudiantes
    ensure_directory(settings.STUDENTS_MEDIA_DIR)
    app.mount('/media/students', StaticFiles(directory=settings.STUDENTS_MEDIA_DIR), name='students_media')


def setup_routes(app: FastAPI) -> None:
    """Configura todas las rutas de la aplicación"""
    # Configurar templates
    templates_path = os.path.join(os.path.dirname(__file__), "templates")
    templates = Jinja2Templates(directory=templates_path)
    
    # Rutas principales
    app.include_router(face_recognition.router)
    app.include_router(students.router)
    app.include_router(attendance.router)
    app.include_router(admin_router)
    app.include_router(reports_router)
    
    # Ruta raíz con interfaz HTML
    @app.get("/", response_class=HTMLResponse)
    async def root(request: Request):
        return templates.TemplateResponse("index.html", {"request": request})


def setup_startup_events(app: FastAPI) -> None:
    """Configura eventos de inicio de la aplicación"""
    @app.on_event("startup")
    def startup_event():
        # Inicializar base de datos
        init_db()
        
        # Crear directorios necesarios
        ensure_directory(settings.DB_FACES_DIR)
        ensure_directory(settings.STUDENTS_MEDIA_DIR)
        ensure_directory(os.path.join(os.path.dirname(__file__), "static"))
        ensure_directory(os.path.join(os.path.dirname(__file__), "templates"))


def setup_health_endpoint(app: FastAPI) -> None:
    """Configura endpoint de salud para Docker healthcheck"""
    @app.get("/health")
    def health_check():
        """Endpoint de salud para Docker healthcheck"""
        return {"status": "healthy", "service": "EDUFACE", "version": settings.VERSION}


# Crear la aplicación
app = create_app()
setup_health_endpoint(app)
