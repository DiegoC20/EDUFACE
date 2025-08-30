# EDUFACE - Despliegue con Docker

## 🐳 Guía de Despliegue Docker

### Prerrequisitos
- Docker instalado
- Docker Compose instalado

### Comandos Disponibles

#### Usando manage.bat (Recomendado)
```bash
.\manage.bat
# Seleccionar opción 6: Docker - Construir imagen
# Seleccionar opción 7: Docker - Ejecutar contenedor
# Seleccionar opción 8: Docker - Detener contenedor
```

#### Comandos Manuales

**1. Construir la imagen:**
```bash
docker build -t eduface:latest .
```

**2. Ejecutar con docker-compose:**
```bash
docker-compose up -d
```

**3. Ver logs:**
```bash
docker-compose logs -f
```

**4. Detener:**
```bash
docker-compose down
```

### Configuración

#### Variables de Entorno
- `TF_ENABLE_ONEDNN_OPTS=0` - Desactiva warnings de TensorFlow
- `PYTHONUNBUFFERED=1` - Salida inmediata de Python

#### Puertos
- **8002** - Puerto de la aplicación FastAPI

#### Volúmenes
- `./data:/app/data` - Persistencia de datos
- `./logs:/app/logs` - Logs de la aplicación

### Healthcheck
El contenedor incluye un healthcheck que verifica:
- URL: `http://localhost:8002/health`
- Intervalo: 30 segundos
- Timeout: 10 segundos
- Reintentos: 3

### Acceso
Una vez iniciado, la aplicación estará disponible en:
- **URL**: http://localhost:8002
- **Health**: http://localhost:8002/health

### Monitoreo
```bash
# Ver estado de contenedores
docker-compose ps

# Ver logs en tiempo real
docker-compose logs -f

# Ver recursos utilizados
docker stats
```

### Troubleshooting

#### Si el contenedor no inicia:
1. Verificar logs: `docker-compose logs`
2. Verificar que el puerto 8002 esté libre
3. Verificar permisos de archivos

#### Si hay errores de dependencias:
1. Reconstruir imagen: `docker build --no-cache -t eduface:latest .`
2. Limpiar volúmenes: `docker-compose down -v`

### Optimizaciones de Producción
- El contenedor usa un usuario no-root para seguridad
- Imagen optimizada con multi-stage no implementado (imagen slim)
- Healthcheck configurado para orquestadores
- Logs estructurados habilitados
