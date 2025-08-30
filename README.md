# 🎓 EDUFACE - Sistema de Asistencia por Reconocimiento Facial

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-green.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

Un sistema moderno y eficiente para el control de asistencia mediante reconocimiento facial, desarrollado con FastAPI y DeepFace.

## ✨ Características Principales

### 🔍 Reconocimiento Facial Avanzado
- **DeepFace**: Reconocimiento facial de alta precisión
- **Múltiples detectores**: OpenCV, RetinaFace, MTCNN
- **Modelos pre-entrenados**: VGGFace, ArcFace optimizados
- **Detección en tiempo real**: Procesamiento rápido de imágenes

### 👥 Gestión de Estudiantes
- **CRUD completo**: Crear, leer, actualizar y eliminar estudiantes
- **Perfiles fotográficos**: Almacenamiento y gestión de imágenes
- **Historial de asistencia**: Seguimiento detallado por estudiante
- **Validación de datos**: Schemas Pydantic para integridad

### 📊 Reportes y Análisis
- **Exportación PDF**: Reportes profesionales con ReportLab
- **Filtros avanzados**: Por fecha, estudiante, estado
- **Estadísticas visuales**: Resúmenes de asistencia
- **Fechas configurables**: Selección automática del día actual

### 🎨 Interfaz de Usuario Moderna
- **Diseño responsivo**: Compatible con dispositivos móviles
- **Modales personalizados**: Sin alertas nativas del navegador
- **Toast notifications**: Feedback visual mejorado
- **Esquema de colores semántico**: Azul (editar), Rojo (eliminar), Verde (guardar)

### 🐳 Docker y DevOps
- **Containerización completa**: Docker y Docker Compose
- **Healthcheck integrado**: Monitoreo automático del servicio
- **Entorno de producción**: Configuración optimizada
- **Escalabilidad**: Preparado para múltiples instancias

## 🚀 Inicio Rápido

### Prerrequisitos
- Python 3.10+
- Docker (opcional)
- Git

### 📦 Instalación Local

1. **Clonar el repositorio**
```bash
git clone https://github.com/DiegoC20/EDUFACE.git
cd EDUFACE
```

2. **Configurar entorno virtual**
```bash
python -m venv .venv_clean
# Windows
.venv_clean\Scripts\activate
# Linux/Mac
source .venv_clean/bin/activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Ejecutar la aplicación**
```bash
uvicorn app.main:app --reload --port 8002
```

5. **Acceder a la aplicación**
- URL: http://localhost:8002
- Health Check: http://localhost:8002/health

### 🐳 Instalación con Docker

1. **Usar manage.bat (Windows)**
```bash
.\manage.bat
# Seleccionar opción 6: Docker - Construir imagen
# Seleccionar opción 7: Docker - Ejecutar contenedor
```

2. **Comandos manuales**
```bash
# Construir y ejecutar
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener
docker-compose down
```

## 🛠️ Herramientas de Desarrollo

### 📋 Script de Gestión (manage.bat)

El proyecto incluye un script de gestión completo con las siguientes opciones:

1. **Iniciar servidor de desarrollo** - Puerto 8002
2. **Limpiar archivos innecesarios** - Script seguro que protege entornos virtuales
3. **Instalar dependencias** - Gestión automática de requirements.txt
4. **Ver estructura del proyecto** - Visualización en árbol
5. **Crear backup** - Compresión automática del proyecto
6. **🆕 Docker - Construir imagen** - Build automatizado
7. **🆕 Docker - Ejecutar contenedor** - docker-compose up
8. **🆕 Docker - Detener contenedor** - docker-compose down

### 🧹 Script de Limpieza

```bash
python clean.py
```

**Características de seguridad:**
- ✅ Protege entornos virtuales (.venv*, node_modules)
- ✅ Solo elimina cache del proyecto (app/**/__pycache__)
- ✅ Limpia modelos temporales de DeepFace
- ✅ Mantiene estructura esencial intacta

## 🏗️ Arquitectura del Proyecto

```
EDUFACE/
├── 📁 app/                     # Aplicación principal
│   ├── 📁 config/             # Configuración centralizada
│   ├── 📁 models/             # Schemas Pydantic
│   ├── 📁 routers/            # Endpoints FastAPI
│   ├── 📁 services/           # Lógica de negocio
│   ├── 📁 static/             # CSS y JavaScript
│   ├── 📁 templates/          # Templates HTML
│   ├── 📁 utils/              # Utilidades y helpers
│   ├── 🐍 main.py             # Punto de entrada
│   └── 🐍 db.py               # Configuración de base de datos
├── 📁 db/                      # Modelos faciales y perfiles
├── 📁 students/               # Imágenes de estudiantes
├── 🐳 Dockerfile             # Imagen Docker optimizada
├── ⚙️ docker-compose.yml      # Orquestación de servicios
├── 🧹 clean.py               # Script de limpieza seguro
├── 📄 manage.bat             # Herramientas de gestión
├── 📝 DOCKER.md             # Documentación Docker
└── 📋 requirements.txt       # Dependencias Python
```

### 🔧 Componentes Técnicos

#### Backend (FastAPI)
- **Framework**: FastAPI con Uvicorn
- **Base de datos**: SQLite con SQLAlchemy
- **Validación**: Pydantic schemas
- **Arquitectura**: Modular con routers separados

#### Reconocimiento Facial
- **DeepFace**: Framework principal de ML
- **TensorFlow**: Motor de deep learning
- **OpenCV**: Procesamiento de imágenes
- **Modelos**: VGGFace, ArcFace pre-entrenados

#### Frontend
- **Vanilla JavaScript**: Sin dependencias externas
- **CSS3**: Diseño moderno y responsivo
- **Jinja2**: Templates del lado del servidor
- **Progressive Enhancement**: Funcionalidad gradual

## 📚 API Endpoints

### 👥 Estudiantes
- `GET /students` - Listar todos los estudiantes
- `POST /students` - Crear nuevo estudiante
- `PUT /students/{id}` - Actualizar estudiante
- `DELETE /students/{id}` - Eliminar estudiante
- `GET /students/{id}/attendance` - Historial de asistencia

### 📸 Reconocimiento
- `POST /attendance/mark` - Marcar asistencia por foto
- `POST /face-recognition/verify` - Verificar identidad

### 📊 Reportes
- `GET /reports/attendance` - Generar reporte de asistencia
- `GET /reports/export-pdf` - Exportar PDF con filtros

### 🏥 Salud del Sistema
- `GET /health` - Estado del servicio (Docker healthcheck)

## ⚙️ Configuración

### Variables de Entorno

```env
# Base de datos
DATABASE_URL=sqlite:///./attendance.sqlite3

# Configuración de la aplicación
APP_TITLE="EDUFACE - Sistema de Asistencia"
APP_VERSION="2.0.0"
DEBUG=False

# Directorios
DB_FACES_DIR="db"
STUDENTS_MEDIA_DIR="students"

# DeepFace
FACE_DETECTOR_BACKEND="opencv"
FACE_RECOGNITION_MODEL="VGGFace"

# Docker específicas
TF_ENABLE_ONEDNN_OPTS=0
PYTHONUNBUFFERED=1
```

### Configuración de Producción

Para entornos de producción, considere:

1. **Base de datos**: Migrar a PostgreSQL/MySQL
2. **Almacenamiento**: Usar servicios de cloud storage
3. **Monitoring**: Implementar logging estructurado
4. **Seguridad**: HTTPS, autenticación JWT
5. **Escalabilidad**: Load balancer, múltiples workers

## 🔒 Seguridad

- **Usuario no-root**: Contenedor Docker con usuario dedicado
- **Validación de entrada**: Schemas Pydantic estrictos
- **Sanitización**: Prevención de inyección de código
- **CORS configurado**: Políticas de origen cruzado
- **Healthcheck**: Monitoreo continuo del servicio

## 🧪 Testing

```bash
# Ejecutar tests (cuando estén disponibles)
pytest tests/ -v

# Test de smoke básico
python -c "import app.main; print('✅ Importación exitosa')"
```

## 📈 Roadmap

### Versión 2.1 (Próxima)
- [ ] Autenticación JWT
- [ ] API REST completa
- [ ] Dashboard de analytics
- [ ] Notificaciones push

### Versión 2.2 (Futura)
- [ ] Machine Learning avanzado
- [ ] Reconocimiento por liveness detection
- [ ] Integración con sistemas LMS
- [ ] App móvil

## 🤝 Contribuciones

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add: AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 👨‍💻 Autor

**Diego Cruzado**
- GitHub: [@DiegoC20](https://github.com/DiegoC20)
- Proyecto: [EDUFACE](https://github.com/DiegoC20/EDUFACE)

## 🙏 Agradecimientos

- [FastAPI](https://fastapi.tiangolo.com/) - Framework web moderno
- [DeepFace](https://github.com/serengil/deepface) - Biblioteca de reconocimiento facial
- [TensorFlow](https://tensorflow.org/) - Plataforma de ML
- [Docker](https://docker.com/) - Containerización

---

⭐ Si este proyecto te resulta útil, ¡dale una estrella en GitHub!

🐛 ¿Encontraste un bug? [Reporta un issue](https://github.com/DiegoC20/EDUFACE/issues)

💡 ¿Tienes una idea? [Inicia una discusión](https://github.com/DiegoC20/EDUFACE/discussions)