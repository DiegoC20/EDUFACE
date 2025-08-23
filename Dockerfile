FROM python:3.10-slim

# Evitar prompts interactivos y mejorar la salida de Python
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Dependencias del sistema necesarias para OpenCV / DeepFace y utilidades
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    curl \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar requirements e instalar (se ejecuta como root para que los binarios queden en /usr/local/bin)
COPY requirements.txt ./
RUN python -m pip install --upgrade pip setuptools wheel \
    && python -m pip install --no-cache-dir -r requirements.txt

# Crear usuario no-root para ejecutar la app y dar permisos sobre /app
RUN useradd --create-home --shell /bin/bash eduface \
    && mkdir -p /app && chown -R eduface:eduface /app

# Copiar el código de la app cambiando propiedad a eduface
COPY --chown=eduface:eduface app ./app
USER eduface

EXPOSE 8000

# Healthcheck simple (usa la raíz /; adapta si tienes /health)
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD curl -f http://127.0.0.1:8000/ || exit 1

# Ejecutar uvicorn (no usar --reload en producción)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
