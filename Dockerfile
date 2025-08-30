FROM python:3.10-slim

# Metadatos de la imagen
LABEL maintainer="Diego Cruzado <diego@eduface.com>" \
      version="1.0" \
      description="EDUFACE - Sistema de asistencia por reconocimiento facial"

# Variables de entorno para optimización
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TF_ENABLE_ONEDNN_OPTS=0

# Instalar dependencias del sistema necesarias para DeepFace y OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    curl \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    ffmpeg \
    libopencv-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements y instalar dependencias Python
COPY requirements.txt ./
RUN python -m pip install --upgrade pip setuptools wheel \
    && python -m pip install --no-cache-dir -r requirements.txt \
    && python -c "import cv2; import deepface; import tensorflow as tf; print('✅ Librerías verificadas')"

# Crear usuario no-root para seguridad
RUN useradd --create-home --shell /bin/bash --user-group eduface \
    && chown -R eduface:eduface /app

# Copiar código de la aplicación
COPY --chown=eduface:eduface app/ ./app/
COPY --chown=eduface:eduface db/ ./db/
COPY --chown=eduface:eduface students/ ./students/

# Crear directorios necesarios
RUN mkdir -p /app/data /app/logs && chown -R eduface:eduface /app/data /app/logs

# Cambiar al usuario no-root
USER eduface

# Exponer puerto
EXPOSE 8002

# Healthcheck mejorado con endpoint específico
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8002/health || exit 1

# Comando para ejecutar la aplicación con configuraciones de producción
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002", "--workers", "1", "--access-log"]
